"""Tests for Sopel's ``youtube`` plugin"""
from __future__ import annotations

import pytest

from sopel.trigger import PreTrigger


TMP_CONFIG = """
[core]
owner = Admin
nick = Sopel
enable =
    youtube
host = irc.libera.chat

[youtube]
api_key = deadbeef
"""


@pytest.fixture
def bot(botfactory, configfactory):
    settings = configfactory('default.ini', TMP_CONFIG)
    return botfactory.preloaded(settings, ['youtube'])


@pytest.mark.parametrize('proto', ('http://', 'https://'))
@pytest.mark.parametrize('base', (
    'youtube.com',
    'www.youtube.com',
))
@pytest.mark.parametrize('path, expected_matches', (
    ('/watch?v=kbLrmesC9x0&list=PLzV2uljPvyAcwIad4RmPAZRgdQNBWHDPp&index=1&pp=iBQA', ('get_video_info', 'get_playlist_info')),
    ('/watch?v=dQw4w9WgXcQ', ('get_video_info',)),
    ('/shorts/dQw4w9WgXcQ/', ('get_video_info',)),
    ('/shorts/dQw4w9WgXcQ', ('get_video_info',)),
    ('/live/dQw4w9WgXcQ/', ('get_video_info',)),
    ('/live/dQw4w9WgXcQ', ('get_video_info',)),
    ('/playlist?list=PLzV2uljPvyAcwIad4RmPAZRgdQNBWHDPp', ('get_playlist_info',)),
))
def test_long_url_matching(proto, base, path, expected_matches, bot):
    link = proto + base + path

    line = PreTrigger(bot.nick, ':User!user@irc.libera.chat PRIVMSG #channel {}'.format(link))
    matched_rules = [
        # we can ignore matches that don't come from this plugin
        match[0].get_rule_label()
        for match in bot.rules.get_triggered_rules(bot, line)
        if match[0].get_plugin_name() == 'youtube'
    ]

    matched_set = set(matched_rules)
    expected_set = set(expected_matches)

    assert len(matched_set) == len(expected_matches)
    assert matched_set == expected_set


@pytest.mark.parametrize('proto', ('http://', 'https://'))
@pytest.mark.parametrize('base', ('youtu.be',))
@pytest.mark.parametrize('trailing_slash', ('/', ''))
def test_short_url_matching(proto, base, trailing_slash, bot):
    link = proto + base + '/dQw4w9WgXcQ' + trailing_slash

    line = PreTrigger(bot.nick, ':User!user@irc.libera.chat PRIVMSG #channel {}'.format(link))
    matched_rules = [
        # we can ignore matches that don't come from this plugin
        match[0].get_rule_label()
        for match in bot.rules.get_triggered_rules(bot, line)
        if match[0].get_plugin_name() == 'youtube'
    ]

    assert len(matched_rules) == 1
    assert matched_rules[0] == 'get_video_info'
