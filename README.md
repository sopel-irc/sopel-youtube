# Sopel YouTube Module

YouTube module for Sopel

## Getting your API key
Go to the [Google Developers Console](https://console.developers.google.com/)
and create an application. When it's created, go to the APIs section, select
the YouTube Data API and enable it. Then go to the Credentials section,
select "Add credentials", pick "API key", and then "Server key". You can enter
a name for it and limit the IPs it can be used from, but you don't have to.
Copy the value it gives you into the prompt in the config wizard, or the
`api_key` value of the config in the `[youtube]` section.
