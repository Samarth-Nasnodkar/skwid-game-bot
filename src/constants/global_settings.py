from enum import Enum


class settingTypes(Enum):
    """
    Enum for setting types.
    """
    MAIN_COMMAND = 0
    MAIN_COMMAND_ARGUMENT = 1
    MAIN_COMMAND_ARGUMENT_LIST = 2
    MAIN_COMMAND_ARGUMENT_DICT = 3


class settingsFormatter:
    BOOLS = ['🟩', '🟥']

    def __init__(self) -> None:
        pass

    def format(self, val, type) -> str:
        if type == settingTypes.MAIN_COMMAND:
            return self.BOOLS[int(val)]


default_settings = {
    "vc_enabled": {
        "name": "Voice Channel Enabled",
        "value": False,
        "desc": "If voice channel sounds are enabled(A voice channel should be specified by the bot manager/admininstrator)",
        "type": settingTypes.MAIN_COMMAND
    },
    "vc": {
        "name": "Voice Channel",
        "value": None,
        "desc": "The voice channel to play sounds in",
        "type": settingTypes.MAIN_COMMAND_ARGUMENT
    },
    "bot_manager_role": {
        "name": "Bot Manager Role",
        "value": None,
        "desc": "The role that is allowed to manage the bot settings",
        "type": settingTypes.MAIN_COMMAND_ARGUMENT
    },
    "custom_roles_enabled": {
        "name": "Custom Game Roles",
        "value": False,
        "desc": "If custom roles for participants, eliminated users and winners should be used",
        "type": settingTypes.MAIN_COMMAND
    },
    "custom_roles": {
        "name": "Custom Game Roles",
        "value": {  # {role_name: role_id}
            "participants": None,
            "eliminated": None,
            "winner": None
        },
        "desc": "The custom roles to use for participants, eliminated users and winners",
        "type": settingTypes.MAIN_COMMAND_ARGUMENT_DICT
    },
    "ignored_channels": {
        "name": "Ignored Channels",
        "value": [],  # channel ids
        "desc": "The channels in which the bot will ignore commands",
        "type": settingTypes.MAIN_COMMAND_ARGUMENT_LIST
    },
    "ignored_users": {
        "name": "Ignored Users",
        "value": [],  # user ids
        "desc": "The users from whom the bot will ignore commands",
        "type": settingTypes.MAIN_COMMAND_ARGUMENT_LIST
    },
    "ignored_roles": {
        "name": "Ignored Roles",
        "value": [],  # role ids
        "desc": "The roles from whom the bot will ignore commands",
        "type": settingTypes.MAIN_COMMAND_ARGUMENT_LIST
    },
    "guild_logs_enabled": {
        "name": "Guild Logs",
        "value": False,
        "desc": "If the bot should log all actions in the server",
        "type": settingTypes.MAIN_COMMAND
    },
    "guild_log_channel": {
        "name": "Guild Log Channel",
        "value": None,
        "desc": "The channel to log all actions in the server",
        "type": settingTypes.MAIN_COMMAND_ARGUMENT
    },
    "bot_updates_on": {
        "name": "Bot Updates",
        "value": False,
        "desc": "If the bot should send the news about major updates to the server",
        "type": settingTypes.MAIN_COMMAND
    },
    "bot_updates_channel": {
        "name": "Bot Updates Channel",
        "value": None,
        "desc": "The channel to send the news about major updates to",
        "type": settingTypes.MAIN_COMMAND_ARGUMENT
    }
}
