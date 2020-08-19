# coding=utf8
"""YouTube plugin for Sopel"""
from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime
from random import random
import re
import sys
from time import sleep

import googleapiclient.discovery
import googleapiclient.errors

from sopel.config.types import (
    ListAttribute,
    StaticSection,
    ValidatedAttribute,
    NO_DEFAULT,
)
from sopel.formatting import color, colors
from sopel.module import commands, example, url
import sopel.tools as tools
import sopel.tools.time

if sys.version_info.major < 3:
    int = long


ISO8601_PERIOD_REGEX = re.compile(
    r"^(?P<sign>[+-])?"
    r"P(?!\b)"
    r"(?P<y>[0-9]+([,.][0-9]+)?(?:Y))?"
    r"(?P<mo>[0-9]+([,.][0-9]+)?M)?"
    r"(?P<w>[0-9]+([,.][0-9]+)?W)?"
    r"(?P<d>[0-9]+([,.][0-9]+)?D)?"
    r"((?:T)(?P<h>[0-9]+([,.][0-9]+)?H)?"
    r"(?P<m>[0-9]+([,.][0-9]+)?M)?"
    r"(?P<s>[0-9]+([,.][0-9]+)?S)?)?$")
regex = re.compile(r'(youtube\.com/watch\S*v=|youtu\.be/)([\w-]+)')
num_retries = 5


def _get_http_error_message(exc):
    if exc.resp.status == 403:
        msg = (
            'YouTube API key not authorized. Please make sure this key is '
            'enabled to access YouTube. (Note: If you have recently made '
            'changes to the API key\'s settings, they may take a few moments '
            'to propagate across Google\'s network.)')
    elif exc.resp.status == 400:
        msg = (
            'YouTube API rejected the configured key. Please make sure the key '
            'has not been truncated or altered accidentally.')
    else:
        msg = (
            'Error setting up YouTube API client. Please check service '
            'status and/or verify API key configuration.')

    return msg


class YoutubeSection(StaticSection):
    api_key = ValidatedAttribute('api_key', default=NO_DEFAULT)
    """The Google API key to auth to the endpoint"""

    info_items = ListAttribute(
        "info_items",
        default=["length", "uploader", "views", "date"],
    )
    """
    The items to include in the video info message, after site and title.
    Available: uploader, date, length, views, comments, and votes_color or votes
    """


def configure(config):
    config.define_section('youtube', YoutubeSection, validate=False)
    config.youtube.configure_setting(
        "api_key", "Enter your Google API key.",
    )
    config.youtube.configure_setting(
        "info_items", "Which attributes to show in response to links"
    )


def setup(bot):
    bot.config.define_section('youtube', YoutubeSection)
    if 'youtube_api_client' not in bot.memory:
        reason = None
        try:
            bot.memory['youtube_api_client'] = googleapiclient.discovery.build(
                "youtube", "v3",
                developerKey=bot.config.youtube.api_key,
                cache_discovery=False)
        except googleapiclient.errors.HttpError as e:
            reason = _get_http_error_message(e)
        if reason:  # TODO: Replace with `raise ... from` when dropping py2
            raise ValueError(reason)
    else:
        # If the memory key is already in use, either we have a plugin conflict
        # or something has gone very wrong. Bail either way.
        raise RuntimeError('youtube_api_client memory key already in use!')


def shutdown(bot):
    bot.memory.pop('youtube_api_client', None)


@commands('yt', 'youtube')
@example('.yt how to be a nerdfighter FAQ')
def search(bot, trigger):
    """Search YouTube"""
    if not trigger.group(2):
        return
    for n in range(num_retries + 1):
        try:
            results = bot.memory['youtube_api_client'].search().list(
                q=trigger.group(2),
                type='video',
                part='id',
                fields='items(id(videoId))',
                maxResults=1,
            ).execute()
        except ConnectionError:
            if n >= num_retries:
                bot.say('Maximum retries exceeded while searching YouTube for '
                        '"{}", please try again later.'.format(trigger.group(2)))
                return
            sleep(random() * 2**n)
            continue
        break
    results = results.get('items')
    if not results:
        bot.say("I couldn't find any YouTube videos for your query.")
        return

    _say_result(bot, trigger, results[0]['id']['videoId'])


@url(regex)
def get_info(bot, trigger, match=None):
    """Get information about the linked YouTube video."""
    match = match or trigger
    _say_result(bot, trigger, match.group(2), include_link=False)


def _say_result(bot, trigger, id_, include_link=True):
    for n in range(num_retries + 1):
        try:
            result = bot.memory['youtube_api_client'].videos().list(
                id=id_,
                part='snippet,contentDetails,liveStreamingDetails,statistics',
                fields=
                    'items('
                        'snippet('
                            'title,channelTitle,liveBroadcastContent,publishedAt'
                        '),'
                        'contentDetails('
                            'duration'
                        '),'
                        'liveStreamingDetails('
                            'actualStartTime,concurrentViewers,scheduledStartTime'
                        '),'
                        'statistics('
                            'viewCount,commentCount,likeCount,dislikeCount'
                        ')'
                    ')',
            ).execute().get('items')
        except ConnectionError:
            if n >= num_retries:
                bot.say('Maximum retries exceeded fetching YouTube video {}, '
                        'please try again later.'.format(id_))
                return
            sleep(random() * 2**n)
            continue
        except googleapiclient.errors.HttpError as e:
            bot.say(_get_http_error_message(e))
            return
        break
    if not result:
        return
    result = result[0]

    # Formatting
    snippet = result['snippet']
    details = result['contentDetails']
    statistics = result['statistics']
    live_info = result.get('liveStreamingDetails', None)
    live_status = snippet["liveBroadcastContent"]

    message = "[YouTube] " + snippet["title"]

    items = bot.config.youtube.info_items
    for item in items:
        if item == "uploader":
            message += " | Channel: " + snippet["channelTitle"]
        elif item == "date":
            if live_status == "none":
                # standard video uploaded in the normal way
                message += " | " + _format_datetime(bot, trigger, snippet["publishedAt"])
            elif live_status == "upcoming":
                # scheduled live stream; show the scheduled start time
                message += " | Scheduled for " + _format_datetime(
                    bot, trigger, live_info["scheduledStartTime"])
            elif live_status == "live":
                # currently live; show when the stream started
                message += " | Live since " + _format_datetime(
                    bot, trigger, live_info["actualStartTime"])
        elif item == "length":
            if live_status == "none":
                # standard video uploaded in the normal way
                message += " | " + _parse_duration(details["duration"])
            elif live_status == "upcoming":
                # skip duration for upcoming broadcasts; they have no length yet
                continue
            elif live_status == "live":
                # currently live; show how long it's been since the start time
                message += " | Live for " + tools.time.seconds_to_human(
                    datetime.utcnow() - _parse_datetime(live_info["actualStartTime"])
                    )[:-4]  # Sopel should make the leading "in"/trailing "ago" optional
        elif item == "views":
            if live_status == "none":
                message += " | {:,} views".format(int(statistics["viewCount"]))
            elif live_status == "upcoming":
                # users can "wait" for a live stream to start, and YouTube will show
                # how many there are on the video page, but that info doesn't appear
                # to be available in API responses (scumbag move alert)
                continue
            elif live_status == "live":
                message += " | {:,} watching".format(int(live_info["concurrentViewers"]))
        elif item == "comments" and "commentCount" in statistics:
            if live_status == "none":
                # live videos tend to have chats, not comments, so only show this
                # if the video is not live-streaming
                message += " | {:,} comments".format(int(statistics["commentCount"]))
        elif item == "votes_color":
            if "likeCount" in statistics:
                likes = int(statistics["likeCount"])
                message += " | " + color("{:,}+".format(likes), colors.GREEN)
            if "dislikeCount" in statistics:
                dislikes = int(statistics["dislikeCount"])
                message += " | " + color("{:,}-".format(dislikes), colors.RED)
        elif item == "votes":
            if "likeCount" in statistics:
                likes = int(statistics["likeCount"])
                message += " | {:,}+".format(likes)
            if "dislikeCount" in statistics:
                dislikes = int(statistics["dislikeCount"])
                message += " | {:,}-".format(dislikes)

    if include_link:
        message = message + ' | Link: https://youtu.be/' + id_
    bot.say(message)


def _parse_duration(duration):
    splitdur = ISO8601_PERIOD_REGEX.match(duration).groupdict()
    dur = ""
    for key in ['y','mo','w','d','h','m','s']:
        if splitdur[key] is not None:
            dur += splitdur[key] + " "
    return dur.lower().strip()


def _parse_datetime(date):
    try:
        dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    return dt


def _format_datetime(bot, trigger, date):
    if type(date) != 'datetime':
        date = _parse_datetime(date)
    return tools.time.format_time(bot.db, bot.config, nick=trigger.nick,
        channel=trigger.sender, time=date)
