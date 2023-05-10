"""Constants for the template_media_player integration."""

from homeassistant.components.media_player import MediaPlayerState

STATES_ON = [
    MediaPlayerState.PLAYING,
    MediaPlayerState.PAUSED,
    MediaPlayerState.BUFFERING,
    MediaPlayerState.IDLE,
    MediaPlayerState.ON,
]

CONF_MEDIA_PLAYERS = "media_players"

# General

CONF_UNIQUE_ID = "unique_id"
CONF_FRIENDLY_NAME = "friendly_name"
CONF_DEVICE_CLASS = "device_class"
CONF_BROWSE_MEDIA_ENTITY_ID = "browse_media_entity_id"
# General Templates

CONF_GLOBAL_TEMPLATE = "global_template"
CONF_AVAILABILITY_TEMPLATE = "availability_template"
CONF_ICON_TEMPLATE = "icon_template"
CONF_STATE_TEMPLATE = "state_template"

CONF_ATTRIBUTE_TEMPLATES = "attribute_templates"
CONF_SERVICE_SCRIPTS = "service_scripts"
CONF_SOUND_MODE_SCRIPTS = "sound_mode_scripts"
CONF_SOURCE_SCRIPTS = "source_scripts"

# Attributes Templates

CONF_ANNOUNCE_TEMPLATE = "announce"
CONF_APP_ID_TEMPLATE = "app_id"
CONF_APP_NAME_TEMPLATE = "app_name"
CONF_ENQUEUE_TEMPLATE = "enqueue"
CONF_ENTITY_PICTURE_TEMPLATE = "entity_picture"
CONF_ENTITY_PICTURE_LOCAL_TEMPLATE = "entity_picture_local"
CONF_EXTRA_TEMPLATE = "extra"
CONF_GROUP_MEMBERS_TEMPLATE = "group_members"
CONF_MEDIA_ALBUM_ARTIST_TEMPLATE = "media_album_artist"
CONF_MEDIA_ALBUM_NAME_TEMPLATE = "media_album_name"
CONF_MEDIA_ARTIST_TEMPLATE = "media_artist"
CONF_MEDIA_CHANNEL_TEMPLATE = "media_channel"
CONF_MEDIA_CONTENT_ID_TEMPLATE = "media_content_id"
CONF_MEDIA_CONTENT_TYPE_TEMPLATE = "media_content_type"
CONF_MEDIA_DURATION_TEMPLATE = "media_duration"
CONF_MEDIA_EPISODE_TEMPLATE = "media_episode"
CONF_MEDIA_IMAGE_HASH_TEMPLATE = "media_image_hash"
CONF_MEDIA_IMAGE_REMOTELY_ACCESSIBLE_TEMPLATE = "media_image_remotely_accessible"
CONF_MEDIA_IMAGE_URL_TEMPLATE = "media_image_url"
CONF_MEDIA_PLAYLIST_TEMPLATE = "media_playlist"
CONF_MEDIA_POSITION_TEMPLATE = "media_position"
CONF_MEDIA_POSITION_UPDATED_AT_TEMPLATE = "media_position_updated_at"
CONF_MEDIA_SEASON_TEMPLATE = "media_season"
CONF_MEDIA_SERIES_TITLE_TEMPLATE = "media_series_title"
CONF_MEDIA_TITLE_TEMPLATE = "media_title"
CONF_MEDIA_TRACK_TEMPLATE = "media_track"
CONF_REPEAT_TEMPLATE = "repeat"
CONF_SEEK_POSITION_TEMPLATE = "seek_position"
CONF_SHUFFLE_TEMPLATE = "shuffle"
CONF_SOUND_MODE_TEMPLATE = "sound_mode"
CONF_SOURCE_TEMPLATE = "source"
CONF_VOLUME_LEVEL_TEMPLATE = "volume_level"
CONF_VOLUME_MUTED_TEMPLATE = "volume_muted"

# Services Scripts

CONF_MEDIA_NEXT_TRACK_SCRIPT = "media_next_track"
CONF_MEDIA_PAUSE_SCRIPT = "media_pause"
CONF_MEDIA_PLAY_SCRIPT = "media_play"
CONF_MEDIA_PLAY_PAUSE_SCRIPT = "media_play_pause"
CONF_MEDIA_PREVIOUS_TRACK_SCRIPT = "media_previous_track"
CONF_MEDIA_SEEK_SCRIPT = "media_seek"
CONF_MEDIA_STOP_SCRIPT = "media_stop"
CONF_REPEAT_SET_SCRIPT = "repeat_set"
CONF_SHUFFLE_SET_SCRIPT = "shuffle_set"
CONF_TOGGLE_SCRIPT = "toggle"
CONF_TURN_OFF_SCRIPT = "turn_off"
CONF_TURN_ON_SCRIPT = "turn_on"
CONF_VOLUME_DOWN_SCRIPT = "volume_down"
CONF_VOLUME_MUTE_SCRIPT = "volume_mute"
CONF_VOLUME_SET_SCRIPT = "volume_set"
CONF_VOLUME_UP_SCRIPT = "volume_up"

CONF_CLEAR_PLAYLIST_SCRIPT = "clear_playlist"
CONF_JOIN_SCRIPT = "join"
CONF_PLAY_MEDIA_SCRIPT = "play_media"
CONF_UNJOIN_SCRIPT = "unjoin"
