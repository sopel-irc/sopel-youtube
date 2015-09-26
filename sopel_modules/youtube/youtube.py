# coding=utf8
"""Youtube module for Sopel"""
from __future__ import unicode_literals, division

from sopel.module import rule, commands, example
from sopel.config.types import StaticSection, ValidatedAttribute, NO_DEFAULT
from sopel import tools
import re
import apiclient.discovery

regex = re.compile('(youtube.com/watch\S*v=|youtu.be/)([\w-]+)')
API = None


class YoutubeSection(StaticSection):
    api_key = ValidatedAttribute('api_key', default=NO_DEFAULT)
    """The Google API key to auth to the endpoint"""


def configure(config):
    config.define_section('youtube', YoutubeSection)
    config.bugzilla.configure_setting(
        'api_key',
        'Enter your Google API key.',
    )


def setup(bot):
    bot.config.define_section('youtube', YoutubeSection)
    if not bot.memory.contains('url_callbacks'):
        bot.memory['url_callbacks'] = tools.WillieMemory()
    bot.memory['url_callbacks'][regex] = get_info
    global API
    API = apiclient.discovery.build("youtube", "v3",
                                    developerKey=bot.config.youtube.api_key)


def shutdown(bot):
    del bot.memory['url_callbacks'][regex]


@commands('yt', 'youtube')
@example('.yt how to be a nerdfighter FAQ')
def search(bot, trigger):
    """Search YouTube"""
    if not trigger.group(2):
        return
    results = API.search().list(
        q=trigger.group(2),
        type='video',
        part='id,snippet',
        maxResults=1,
    ).execute()
    results = results.get('items')
    if not results:
        bot.say("I couldn't find any YouTube videos for your query.")
        return

    _say_result(bot, results[0]['id']['videoId'], True)


@rule('.*(youtube.com/watch\S*v=|youtu.be/)([\w-]+).*')
def get_info(bot, trigger, found_match=None):
    """
    Get information about the latest video uploaded by the channel provided.
    """
    match = found_match or trigger
    _say_result(bot, match.group(2), False)


def _say_result(bot, id_, include_link):
    result = API.videos().list(
        id=id_,
        part='snippet,contentDetails,statistics',
    ).execute().get('items')
    if not result:
        return
    result = result[0]

    message = (
        '[YouTube] Title: {title} | Uploader: {uploader} | Length: {length} | '
        'Uploaded: {uploaded} | Views: {views}'
    )

    snippet = result['snippet']
    details = result['contentDetails']
    duration = _parse_duration(details['duration'])
    uploaded = _parse_published_at(snippet['publishedAt'])

    message = message.format(
        title=snippet['title'],
        uploader=snippet['channelTitle'],
        length=duration,
        uploaded=uploaded,
        views=result['statistics']['viewCount'],
    )
    if include_link:
        message = message + ' | Link: https://youtu.be/' + id_
    bot.say(message)


def _parse_duration(duration):
    values = re.split('\D+', duration)[1:-1]
    return ':'.join(values)


def _parse_published_at(published):
    return published  # TODO make this nicer
