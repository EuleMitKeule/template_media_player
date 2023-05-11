[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Code Quality](https://github.com/EuleMitKeule/template_media_player/actions/workflows/quality.yml/badge.svg?branch=master)](https://github.com/EuleMitKeule/template_media_player/actions/workflows/quality.yml)

# Template Media Player

> Note: This integration is strongly inspired by [media_player.template](https://github.com/Sennevds/media_player.template).<br>
> Unfortunately that integration is no longer maintained and missing some features, so I decided to create a new and improved one.

Template Media Player allows you to create media player entities in Home Assistant using templates and scripts.<br>
You can define any attribute you want and create custom behaviour for all services supported by the `media_player` domain. 

## Installation

You can install this integration using the custom repository option in [HACS](https://hacs.xyz/).<br>

1. Add the repository URL to the list of custom repositories in HACS
2. Select and install the integration in HACS
3. Restart Home Assistant
4. Configure your entities

## Configuration

To create the entities you need to define them in your `configuration.yaml` file.<br>
For a full example of all available options see [examples](examples/configuration.yaml).

```yaml
media_player:
  - platform: template_media_player
    media_players:
      my_media_player:
        unique_id: my_media_player
        friendly_name: My Media Player
        device_class: tv
        icon_template: mdi:television
        state_template: "on"
```

### Templates

Options that are marked as `_template` or elements of the `attribute_templates` object can be defined using Jinja2 templates:

```yaml
# ...
state_template: >
  {% if states('media_player.something") == "on" %}
    idle
  {% else %}
    off
  {% endif %}
```

#### Attributes

To define state attributes for your entity use the `attribute_templates` option.<br>
You can use the variable `attribute` in your templates to get the current attributes name as a string.<br>
For a full list of attributes commonly used by media player entities see [examples](examples/configuration.yaml).

```yaml
media_player:
  - platform: template_media_player
    media_players:
      my_media_player:
        #...
        attribute_templates:
            media_title: >
              # attribute contains the value "media_title"
              {{ state_attr("media_player.something", attribute) }}
```

#### Global Template

To reduce code duplication you can define a template using the `global_template` option.
This template will be executed before each of the other templates and can be used to define common variables.

```yaml
media_player:
  - platform: template_media_player
    media_players:
      my_media_player:
        #...
        global_template: >
          {% set tv = "media_player.tv" %}
        state_template: >
          {{ states(tv) }}
```

### Scripts

Elements of the `service_scripts`, `source_scripts` or `sound_mode_scripts` options are action sequences like in Home Assistant scripts.

```yaml
media_player:
  - platform: template_media_player
    media_players:
      my_media_player:
        #...
        source_scripts:
          Plex:
            - service: media_player.turn_on
              data_template:
                entity_id: media_player.tv
            - delay:
                seconds: 3
            - service: media_player.select_source
              data_template:
                entity_id: media_player.tv
                source: Plex
```

#### Service Scripts

Use the `service_scripts` option to define services that are supported by the `media_player` domain.<br>
For a full list of services and their respective variables supported by media player entities see [examples](examples/configuration.yaml).

```yaml
media_player:
  - platform: template_media_player
    media_players:
      my_media_player:
        #...
        service_scripts:
          turn_on:
            - service: media_player.turn_on
              data_template:
                entity_id: media_player.tv
```

#### Source Scripts

Use the `source_scripts` option to define sources for your media_player.

```yaml
media_player:
  - platform: template_media_player
    media_players:
      my_media_player:
        #...
        source_scripts:
          Plex:
            - service: media_player.select_source
              data_template:
                entity_id: media_player.tv
                source: Plex
```

#### Sound Mode Scripts

Use the `sound_mode_scripts` option to define sound modes for your media_player.

```yaml
media_player:
  - platform: template_media_player
    media_players:
      my_media_player:
        #...
        sound_mode_scripts:
          Bass Boost:
            - service: media_player.select_sound_mode
              data_template:
                entity_id: media_player.soundbar
                source: Bass Boost
```

### Browse Media

You can specify an entity to use for the browse media functionality using the `browse_media_entity_id` option.<br>
Make sure you also define the `play_media` service for this to work.
