# sopel-youtube

YouTube link information plugin for Sopel.

## Installing

Releases are hosted on PyPI, so after installing Sopel, all you need is `pip`:

```shell
$ pip install sopel-youtube
```

(Make sure you use the "correct" `pip`, i.e. the one corresponding to the Python
environment where you have Sopel installed.)

### Migrating from `sopel-modules.youtube`

You can simply `pip uninstall sopel-modules.youtube` prior to installing this
package; no extra steps should be needed. `sopel-youtube` inherits the
configuration section originally defined and used by the older versions.

### Latest source

If you want to help develop or test the plugin, you'll need to install from
source. Clone the repo first, then:

```shell
$ pip install -e .
```

#### Testing changes

To run tests, make sure you have the development dependencies as well:

```shell
$ pip install -r dev-requirements.txt
```

Run the test suite from the repo root directory:

```shell
$ pytest -v .
```

## Getting your API key
Go to the [Google Developers Console](https://console.developers.google.com/)
and create an application. When it's created, go to the APIs section, select
the YouTube Data API and enable it. Then go to the Credentials section,
select "Add credentials", pick "API key", and then "Server key". You can enter
a name for it and limit the IPs it can be used from, but you don't have to.
Copy the value it gives you into the prompt in the config wizard (see below),
or the `api_key` field of the config file's `[youtube]` section.

## Configuring the plugin

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
