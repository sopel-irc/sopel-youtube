# sopel-youtube

YouTube plugin for Sopel

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
