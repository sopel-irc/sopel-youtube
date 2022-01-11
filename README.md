# sopel-youtube

YouTube info plugin for Sopel

## Installing

If possible, use `pip` to install this plugin. Below are example commands; you
might need to add `sudo` and/or call a different `pip` (e.g. `pip3`) depending
on your system and environment. Do not use `setup.py install`; Sopel won't be
able to load the plugin correctly.

### Published release

    pip install sopel_modules.youtube

### From source

    # Clone the repo, then run this in /path/to/sopel-youtube
    pip install .

## Getting your API key
Go to the [Google Developers Console](https://console.developers.google.com/)
and create an application. When it's created, go to the APIs section, select
the YouTube Data API and enable it. Then go to the Credentials section,
select "Add credentials", pick "API key", and then "Server key". You can enter
a name for it and limit the IPs it can be used from, but you don't have to.
Copy the value it gives you into the prompt in the config wizard, or the
`api_key` value of the config in the `[youtube]` section.

## Config settings
`sopel-youtube` supports Sopel's interactive configuration wizard:

    sopel-plugins configure youtube

The `api_key` option is self-explanatory (see above).

If video "watch" links contain a playlist ID, the plugin will show the
playlist info as well as the video info by default. To disable this, set
`playlist_watch` to `False`.

For videos, by default, only the video length, uploader (channel name), view
count, and upload date are shown. The included items, and the order in which
they appear, depend on the `info_items` setting, which is a list of keywords.
Unrecognized keywords are simply ignored. Supported `info_items` are:

* `comments` (comment count)
* `date` (upload time/date)
* `length` (duration)
* `likes` (count)
* `uploader` (channel name)
* `views` (view count)

### Legacy `info_items`
Prior to YouTube's removal of public dislike counts, there were two vote-related
`info_items`: `votes` and `votes_color`. These keywords are deprecated as of
`sopel-youtube` 0.4.3. They will function as aliases to the new `likes` keyword
until they are removed entirely in v0.5 or thereabouts.
