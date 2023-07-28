"""Contains the template_media_player entity class and configuration."""

import logging
from typing import Any, Optional

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.media_player import DOMAIN as DOMAIN_MEDIA_PLAYER
from homeassistant.components.media_player import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
    RepeatMode,
)
from homeassistant.components.media_player.browse_media import BrowseMedia
from homeassistant.components.template import DOMAIN, PLATFORMS
from homeassistant.components.template.template_entity import TemplateEntity
from homeassistant.const import ATTR_FRIENDLY_NAME, CONF_ENTITY_PICTURE_TEMPLATE
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.reload import async_setup_reload_service
from homeassistant.helpers.script import Script
from homeassistant.helpers.template import Template
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    CONF_ATTRIBUTE_TEMPLATES,
    CONF_AVAILABILITY_TEMPLATE,
    CONF_BASE_MEDIA_PLAYER_ENTITY_ID,
    CONF_BROWSE_MEDIA_ENTITY_ID,
    CONF_CLEAR_PLAYLIST_SCRIPT,
    CONF_DEVICE_CLASS,
    CONF_FRIENDLY_NAME,
    CONF_GLOBAL_TEMPLATE,
    CONF_ICON_TEMPLATE,
    CONF_JOIN_SCRIPT,
    CONF_MEDIA_NEXT_TRACK_SCRIPT,
    CONF_MEDIA_PAUSE_SCRIPT,
    CONF_MEDIA_PLAY_PAUSE_SCRIPT,
    CONF_MEDIA_PLAY_SCRIPT,
    CONF_MEDIA_PLAYERS,
    CONF_MEDIA_PREVIOUS_TRACK_SCRIPT,
    CONF_MEDIA_SEEK_SCRIPT,
    CONF_MEDIA_STOP_SCRIPT,
    CONF_PLAY_MEDIA_SCRIPT,
    CONF_REPEAT_SET_SCRIPT,
    CONF_SERVICE_SCRIPTS,
    CONF_SHUFFLE_SET_SCRIPT,
    CONF_SOUND_MODE_SCRIPTS,
    CONF_SOURCE_SCRIPTS,
    CONF_STATE_TEMPLATE,
    CONF_TOGGLE_SCRIPT,
    CONF_TURN_OFF_SCRIPT,
    CONF_TURN_ON_SCRIPT,
    CONF_UNIQUE_ID,
    CONF_UNJOIN_SCRIPT,
    CONF_VOLUME_DOWN_SCRIPT,
    CONF_VOLUME_MUTE_SCRIPT,
    CONF_VOLUME_SET_SCRIPT,
    CONF_VOLUME_UP_SCRIPT,
    STATES_ON,
)

_LOGGER = logging.getLogger(__name__)

MEDIA_PLAYER_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_UNIQUE_ID): cv.string,
        vol.Optional(CONF_FRIENDLY_NAME): cv.string,
        vol.Optional(CONF_DEVICE_CLASS): cv.string,
        vol.Optional(CONF_BASE_MEDIA_PLAYER_ENTITY_ID): cv.entity_id,
        vol.Optional(CONF_BROWSE_MEDIA_ENTITY_ID): cv.entity_id,
        vol.Optional(CONF_GLOBAL_TEMPLATE): cv.template,
        vol.Optional(CONF_AVAILABILITY_TEMPLATE): cv.template,
        vol.Optional(CONF_ICON_TEMPLATE): cv.template,
        vol.Optional(CONF_STATE_TEMPLATE): cv.template,
        vol.Optional(CONF_ATTRIBUTE_TEMPLATES, default={}): {cv.string: cv.template},
        vol.Optional(CONF_SERVICE_SCRIPTS, default={}): {cv.string: cv.SCRIPT_SCHEMA},
        vol.Optional(CONF_SOUND_MODE_SCRIPTS, default={}): {
            cv.string: cv.SCRIPT_SCHEMA
        },
        vol.Optional(CONF_SOURCE_SCRIPTS, default={}): {cv.string: cv.SCRIPT_SCHEMA},
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_MEDIA_PLAYERS): cv.schema_with_slug_keys(MEDIA_PLAYER_SCHEMA)}
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType = None,
):
    """Set up the template media players."""

    _ = discovery_info

    await async_setup_reload_service(hass, DOMAIN, PLATFORMS)
    async_add_entities(await _async_create_entities(hass, config))


async def _async_create_entities(hass: HomeAssistant, config: ConfigType):
    """Create the template media players."""

    media_players = []

    for media_player_name, media_player_config in config[CONF_MEDIA_PLAYERS].items():
        domain: str = __name__.split(".")[-2]
        unique_id: str = media_player_config.get(CONF_UNIQUE_ID, media_player_name)
        friendly_name: str = media_player_config.get(
            ATTR_FRIENDLY_NAME, media_player_name
        )
        device_class: MediaPlayerDeviceClass | None = media_player_config.get(
            CONF_DEVICE_CLASS
        )
        base_media_player_entity_id: str | None = media_player_config.get(
            CONF_BASE_MEDIA_PLAYER_ENTITY_ID
        )
        browse_media_entity_id: str | None = media_player_config.get(
            CONF_BROWSE_MEDIA_ENTITY_ID
        )
        global_template: Template | None = media_player_config.get(CONF_GLOBAL_TEMPLATE)
        availability_template: Template | None = media_player_config.get(
            CONF_AVAILABILITY_TEMPLATE
        )
        icon_template: Template = media_player_config.get(CONF_ICON_TEMPLATE)
        state_template: Template = media_player_config.get(CONF_STATE_TEMPLATE)
        attribute_templates: dict[str, Template] = media_player_config.get(
            CONF_ATTRIBUTE_TEMPLATES
        )
        service_scripts: dict[str, Any] = {
            service: Script(hass, service_script, friendly_name, domain)
            for service, service_script in media_player_config.get(
                CONF_SERVICE_SCRIPTS
            ).items()
        }
        sound_mode_scripts: dict[str, Any] = {
            sound_mode: Script(hass, sound_mode_script, friendly_name, domain)
            for sound_mode, sound_mode_script in media_player_config.get(
                CONF_SOUND_MODE_SCRIPTS
            ).items()
        }
        source_scripts: dict[str, Any] = {
            source: Script(hass, source_script, friendly_name, domain)
            for source, source_script in media_player_config.get(
                CONF_SOURCE_SCRIPTS
            ).items()
        }

        if global_template is not None:
            if availability_template is not None:
                availability_template = Template(
                    global_template.template + availability_template.template, hass
                )
            if icon_template is not None:
                icon_template = Template(
                    global_template.template + icon_template.template, hass
                )
            if state_template is not None:
                state_template = Template(
                    global_template.template + state_template.template, hass
                )
            for attribute, attribute_template in attribute_templates.items():
                attribute_templates[attribute] = Template(
                    global_template.template + attribute_template.template, hass
                )

        for attribute, attribute_template in attribute_templates.items():
            attribute_templates[attribute] = Template(
                '{% set attribute = "'
                + attribute
                + '" %}'
                + attribute_template.template,
                hass,
            )

        if icon_template is not None:
            icon_template = Template(
                '{% set attribute = "icon" %}' + icon_template.template,
                hass,
            )

        if availability_template is not None:
            availability_template = Template(
                '{% set attribute = "availability" %}' + availability_template.template,
                hass,
            )

        media_players.append(
            TemplateMediaPlayer(
                hass,
                domain,
                media_player_name,
                unique_id,
                friendly_name,
                device_class,
                base_media_player_entity_id,
                browse_media_entity_id,
                global_template,
                availability_template,
                icon_template,
                state_template,
                attribute_templates,
                service_scripts,
                sound_mode_scripts,
                source_scripts,
            )
        )

    return media_players


class TemplateMediaPlayer(TemplateEntity, MediaPlayerEntity):
    """Representation of a Template Media player."""

    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        media_player_name: str,
        unique_id: str,
        friendly_name: str,
        device_class: Optional[MediaPlayerDeviceClass],
        base_media_player_entity_id: Optional[str],
        browse_media_entity_id: Optional[str],
        global_template: Optional[Template],
        availability_template: Optional[Template],
        icon_template: Optional[Template],
        state_template: Optional[Template],
        attribute_templates: dict[str, Template],
        service_scripts: dict[str, Script],
        sound_mode_scripts: Optional[dict[str, Any]],
        source_scripts: Optional[dict[str, Any]],
    ) -> None:
        """Initialize the Template Media player."""

        self.hass = hass
        self._domain = domain
        self._media_player_name = media_player_name
        self._friendly_name = friendly_name
        self.entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, media_player_name, hass=hass
        )
        self._unique_id = unique_id
        self._device_class = device_class
        self._base_media_player_entity_id = base_media_player_entity_id
        self._browse_media_entity_id = browse_media_entity_id
        self._global_template = global_template
        self._availability_template = availability_template
        self._icon_template = icon_template
        self._state_template = state_template
        self._attribute_templates = attribute_templates
        self._service_scripts = service_scripts
        self._sound_mode_scripts = sound_mode_scripts
        self._source_scripts = source_scripts
        self._state = MediaPlayerState.OFF

        availability_template = attribute_templates.pop(
            CONF_AVAILABILITY_TEMPLATE, None
        )
        icon_template = attribute_templates.pop(CONF_ICON_TEMPLATE, None)
        entity_picture_template = attribute_templates.pop(
            CONF_ENTITY_PICTURE_TEMPLATE, None
        )

        super().__init__(
            hass,
            attribute_templates=attribute_templates,
            availability_template=availability_template,
            icon_template=icon_template,
            entity_picture_template=entity_picture_template,
            unique_id=unique_id,
            fallback_name=friendly_name,
        )

    async def async_added_to_hass(self):
        """Register callbacks."""

        self.add_template_attribute(
            "_state", self._state_template, None, self._update_state
        )
        await super().async_added_to_hass()

    @property
    def base_media_player_entity(self) -> MediaPlayerEntity | None:
        if self._base_media_player_entity_id is not None:
            component: EntityComponent[MediaPlayerEntity] = self.hass.data[
                DOMAIN_MEDIA_PLAYER
            ]
            if entity := component.get_entity(self._base_media_player_entity_id):
                return entity
        return None

    @property
    def browse_media_entity(self) -> MediaPlayerEntity | None:
        if self._browse_media_entity_id is not None:
            component: EntityComponent[MediaPlayerEntity] = self.hass.data[
                DOMAIN_MEDIA_PLAYER
            ]
            if entity := component.get_entity(self._browse_media_entity_id):
                return entity
        return None

    @property
    def name(self):
        """Return the name of the media player."""
        return self._friendly_name

    @property
    def device_class(self):
        """Return the class of this device."""

        if self._device_class is not None:
            return self._device_class

        if self.base_media_player_entity is not None:
            return self.base_media_player_entity.device_class

        return None

    @property
    def is_on(self):
        """Return true if device is on."""
        return self.state in STATES_ON

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def supported_features(self):
        """Flag media player features that are supported."""

        support = 0

        if self.base_media_player_entity is not None:
            support |= self.base_media_player_entity.supported_features

        if CONF_MEDIA_PAUSE_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.PAUSE
        if CONF_MEDIA_SEEK_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.SEEK
        if CONF_VOLUME_SET_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.VOLUME_SET
        if CONF_VOLUME_MUTE_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.VOLUME_MUTE
        if CONF_MEDIA_PREVIOUS_TRACK_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.PREVIOUS_TRACK
        if CONF_MEDIA_NEXT_TRACK_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.NEXT_TRACK
        if CONF_TURN_ON_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.TURN_ON
        if CONF_TURN_OFF_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.TURN_OFF
        if CONF_PLAY_MEDIA_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.PLAY_MEDIA
        if (
            CONF_VOLUME_UP_SCRIPT in self._service_scripts
            and CONF_VOLUME_DOWN_SCRIPT in self._service_scripts
        ):
            support |= MediaPlayerEntityFeature.VOLUME_STEP
        if len(self.source_list) > 0:
            support |= MediaPlayerEntityFeature.SELECT_SOURCE
        if CONF_MEDIA_STOP_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.STOP
        if CONF_CLEAR_PLAYLIST_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.CLEAR_PLAYLIST
        if CONF_MEDIA_PLAY_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.PLAY
        if CONF_SHUFFLE_SET_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.SHUFFLE_SET
        if len(self.sound_mode_list) > 0:
            support |= MediaPlayerEntityFeature.SELECT_SOUND_MODE
        if self._browse_media_entity_id is not None:
            support |= MediaPlayerEntityFeature.BROWSE_MEDIA
        if CONF_REPEAT_SET_SCRIPT in self._service_scripts:
            support |= MediaPlayerEntityFeature.REPEAT_SET
        if (
            CONF_JOIN_SCRIPT in self._service_scripts
            and CONF_UNJOIN_SCRIPT in self._service_scripts
        ):
            support |= MediaPlayerEntityFeature.GROUPING

        return support

    @property
    def state(self) -> MediaPlayerState | None:
        if self._state_template is not None:
            return self._state

        if self.base_media_player_entity is not None:
            return self.base_media_player_entity.state

        return None

    @property
    def source_list(self) -> list[str]:
        if self._source_scripts is not None:
            return list(self._source_scripts.keys())

        if self.base_media_player_entity is not None:
            return self.base_media_player_entity.source_list

        return []

    @property
    def sound_mode_list(self) -> list | list[str] | None:
        if self._sound_mode_scripts is None:
            return list(self._sound_mode_scripts.keys())

        if self.base_media_player_entity is not None:
            return self.base_media_player_entity.sound_mode_list

        return []

    @callback
    def _update_state(self, result: str | TemplateError) -> None:
        super()._update_state(result)

        if isinstance(result, TemplateError):
            _LOGGER.error(f"Could not render state template: {result}")
            self._state = None
            return

        try:
            state = MediaPlayerState(result)
            self._state = state
        except ValueError:
            _LOGGER.error(f"Received invalid state: {result}")
            state = None

    async def async_media_next_track(self) -> None:
        if CONF_MEDIA_NEXT_TRACK_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_MEDIA_NEXT_TRACK_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_media_next_track()

    async def async_media_pause(self):
        if CONF_MEDIA_PAUSE_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_MEDIA_PAUSE_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_media_pause()

    async def async_media_play(self):
        if CONF_MEDIA_PLAY_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_MEDIA_PLAY_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_media_play()

    async def async_media_play_pause(self):
        if CONF_MEDIA_PLAY_PAUSE_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_MEDIA_PLAY_PAUSE_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_media_play_pause()

    async def async_media_previous_track(self):
        if CONF_MEDIA_PREVIOUS_TRACK_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_MEDIA_PREVIOUS_TRACK_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_media_previous_track()

    async def async_media_seek(self, position):
        if CONF_MEDIA_SEEK_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_MEDIA_SEEK_SCRIPT].async_run(
                {"position": position}, context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_media_seek(position)

    async def async_media_stop(self):
        if CONF_MEDIA_STOP_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_MEDIA_STOP_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_media_stop()

    async def async_set_repeat(self, repeat: RepeatMode):
        if CONF_REPEAT_SET_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_REPEAT_SET_SCRIPT].async_run(
                {"repeat": repeat}, context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_set_repeat(repeat)

    async def async_set_shuffle(self, shuffle: bool):
        if CONF_SHUFFLE_SET_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_SHUFFLE_SET_SCRIPT].async_run(
                {"shuffle": shuffle}, context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_set_shuffle(shuffle)

    async def async_toggle(self) -> None:
        if CONF_TOGGLE_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_TOGGLE_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_toggle()

    async def async_turn_off(self):
        if CONF_TURN_OFF_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_TURN_OFF_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_turn_off()

    async def async_turn_on(self):
        if CONF_TURN_ON_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_TURN_ON_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_turn_on()

    async def async_volume_down(self):
        if CONF_VOLUME_DOWN_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_VOLUME_DOWN_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_volume_down()

    async def async_mute_volume(self, mute):
        if CONF_VOLUME_MUTE_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_VOLUME_MUTE_SCRIPT].async_run(
                {"mute": mute}, context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_mute_volume(mute)

    async def async_set_volume_level(self, volume):
        if CONF_VOLUME_SET_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_VOLUME_SET_SCRIPT].async_run(
                {"volume": volume}, context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_set_volume_level(volume)

    async def async_volume_up(self):
        if CONF_VOLUME_UP_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_VOLUME_UP_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_volume_up()

    async def async_clear_playlist(self):
        if CONF_CLEAR_PLAYLIST_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_CLEAR_PLAYLIST_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_clear_playlist()

    async def async_join_players(self, group_members: list[str]):
        if CONF_JOIN_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_JOIN_SCRIPT].async_run(
                {"group_members": group_members}, context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_join_players(group_members)

    async def async_play_media(
        self, media_type: MediaType | str, media_id: str, **kwargs
    ):
        if CONF_PLAY_MEDIA_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_PLAY_MEDIA_SCRIPT].async_run(
                {"media_type": media_type, "media_id": media_id}, context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_play_media(
                media_type, media_id, **kwargs
            )

    async def async_select_sound_mode(self, sound_mode):
        if sound_mode not in self.sound_mode_list:
            return

        if self._sound_mode_scripts is not None:
            await self._sound_mode_scripts[sound_mode].async_run(context=self._context)

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_select_sound_mode(sound_mode)

    async def async_select_source(self, source):
        if source not in self.source_list:
            return

        if self._source_scripts is not None:
            await self._source_scripts[source].async_run(context=self._context)

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_select_source(source)

    async def async_unjoin_player(self):
        if CONF_UNJOIN_SCRIPT in self._service_scripts:
            await self._service_scripts[CONF_UNJOIN_SCRIPT].async_run(
                context=self._context
            )

        if self.base_media_player_entity is not None:
            await self.base_media_player_entity.async_unjoin_player()

    async def async_browse_media(
        self,
        media_content_type: MediaType | str | None = None,
        media_content_id: str | None = None,
    ) -> BrowseMedia:
        if self.browse_media_entity is not None:
            return await self.browse_media_entity.async_browse_media(
                media_content_type, media_content_id
            )

        if self.base_media_player_entity is not None:
            return await self.base_media_player_entity.async_browse_media(
                media_content_type, media_content_id
            )
