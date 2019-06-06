# coding=utf8
"""Youtube module for Sopel"""
from __future__ import unicode_literals, division

from sopel.module import rule, commands, example
from sopel.config.types import StaticSection, ValidatedAttribute, NO_DEFAULT
from sopel.formatting import color, colors
from sopel import tools
import datetime
import sys
import re
import apiclient.discovery
if sys.version_info.major < 3:
    int = long

from time import sleep
from random import random

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
regex = re.compile('(youtube.com/watch\S*v=|youtu.be/)([\w-]+)')
API = None
num_retries = 5


class YoutubeSection(StaticSection):
    api_key = ValidatedAttribute('api_key', default=NO_DEFAULT)
    """The Google API key to auth to the endpoint"""


def configure(config):
    config.define_section('youtube', YoutubeSection, validate=False)
    config.youtube.configure_setting(
        'api_key',
        'Enter your Google API key.',
    )


def setup(bot):
    bot.config.define_section('youtube', YoutubeSection)
    if 'url_callbacks' not in bot.memory:
        bot.memory['url_callbacks'] = tools.SopelMemory()
    bot.memory['url_callbacks'][regex] = get_info
    global API
    API = apiclient.discovery.build("youtube", "v3",
                                    developerKey=bot.config.youtube.api_key,
                                    cache_discovery=False)


def shutdown(bot):
    del bot.memory['url_callbacks'][regex]


@commands('yt', 'youtube')
@example('.yt how to be a nerdfighter FAQ')
def search(bot, trigger):
    """Search YouTube"""
    if not trigger.group(2):
        return
    for n in range(num_retries + 1):
        try:
            results = API.search().list(
                q=trigger.group(2),
                type='video',
                part='id,snippet',
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


@rule('.*(youtube.com/watch\S*v=|youtu.be/)([\w-]+).*')
def get_info(bot, trigger, found_match=None):
    """
    Get information about the latest video uploaded by the channel provided.
    """
    match = found_match or trigger
    _say_result(bot, trigger, match.group(2), include_link=False)


def _say_result(bot, trigger, id_, include_link=True):
    for n in range(num_retries + 1):
        try:
            result = API.videos().list(
                id=id_,
                part='snippet,contentDetails,statistics',
            ).execute().get('items')
        except ConnectionError:
            if n >= num_retries:
                bot.say('Maximum retries exceeded fetching YouTube video {},'
                        ' please try again later.'.format(id_))
                return
            sleep(random() * 2**n)
            continue
        break
    if not result:
        return
    result = result[0]

    message = (
        '[You' + color('Tube', colors.WHITE, colors.RED)  + '] '
        '{title} | Uploader: {uploader} | Uploaded: {uploaded} | '
        'Length: {length} | Views: {views:,} | Comments: {comments}'
    )

    snippet = result['snippet']
    details = result['contentDetails']
    statistics = result['statistics']
    duration = _parse_duration(details['duration'])
    uploaded = _parse_published_at(bot, trigger, snippet['publishedAt'])
    comments = statistics.get('commentCount', '-')
    if comments != '-':
        comments = '{:,}'.format(int(comments))

    message = message.format(
        title=snippet['title'],
        uploader=snippet['channelTitle'],
        length=duration,
        uploaded=uploaded,
        views=int(statistics['viewCount']),
        comments=comments,
    )
    if 'likeCount' in statistics:
        likes = int(statistics['likeCount'])
        message += ' | ' + color('{:,}+'.format(likes), colors.GREEN)
    if 'dislikeCount' in statistics:
        dislikes = int(statistics['dislikeCount'])
        message += ' | ' + color('{:,}-'.format(dislikes), colors.RED)
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


def _parse_published_at(bot, trigger, published):
    pubdate = datetime.datetime.strptime(published, '%Y-%m-%dT%H:%M:%S.%fZ')
    return tools.time.format_time(bot.db, bot.config, nick=trigger.nick, 
        channel=trigger.sender, time=pubdate)
