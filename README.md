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

1. Go to the [Google Cloud APIs & Services Console][cloud-api-console] and
   create a new project for your bot (or select an existing one, if you prefer).
2. [Visit the API Library][api-library-query], find "YouTube Data API v3" (or
   [click here][api-library-direct]), and enable it.
3. Go to the [Credentials section][api-credentials], click "+ Create
   Credentials", and choose "API key" from the menu. You can enter a name for
   the new key and limit the IPs it can be used from, but you don't have to.
4. Copy the new key and paste it into the appropriate prompt in the config
   wizard (see below), or the `api_key` field under `[youtube]` in your bot's
   config file.
5. **Optional:** If the ⚠️ icon next to your new key in the Cloud Console annoys
   you, it changes to a checkmark if you [restrict][api-key-restrictions] the
   key's access to only the API(s) it needs.

[cloud-api-console]: https://console.cloud.google.com/apis/dashboard
[api-library-query]: https://console.cloud.google.com/apis/library/browse?q=youtube
[api-library-direct]: https://console.cloud.google.com/apis/library/youtube.googleapis.com
[api-credentials]: https://console.cloud.google.com/apis/credentials
[api-key-restrictions]: https://cloud.google.com/docs/authentication/api-keys#adding-api-restrictions

## Configuring the plugin

`sopel-youtube` supports Sopel's interactive configuration wizard:

    sopel-plugins configure youtube

The `api_key` option is self-explanatory (see above for how to get one).

If video "watch" links contain a playlist ID, the plugin will show the
playlist info as well as the video info by default. To disable this, set
`playlist_watch` to `False`.

If video "watch" links contain a comment ID, the plugin will **only** show info
about the comment by default. If you also want video info posted in this
situation, set `comment_watch` to `True`.

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
