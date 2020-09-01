from voluptuous import Schema, Required, REMOVE_EXTRA, Url, Invalid

config_schema = Schema(
    {
        Required("host"): Url(),
        Required("bans"): [str]
    },
    extra=REMOVE_EXTRA
)