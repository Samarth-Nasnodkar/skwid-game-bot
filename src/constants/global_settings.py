default_settings = {
    # If Voice Channel sounds are enabled(A voice channel should be specified by the bot manager/admininstrator)
    "vc_enabled": False,
    "vc": None,  # The ID of the Voice Channel to play sounds in
    # The ID of the role that is allowed to manage the bot settings. Defaults to the server manager
    "bot_manager_role": None,
    # If custom roles for participants, eliminated users and winners should be used.
    "custom_roles_enabled": False,
    "custom_roles": {  # The Custom roles. If not already present, the bot can create them. Manage Roles permission is required.
        "participants": None,
        "eliminated": None,
        "winner": None
    },
    # The channels in which the bot will ignore commands.
    "ignored_channels": [],
    "ignored_users": [],  # The users that the bot will ignore commands from.
    # The users belonding to the roles that the bot will ignore commands from.
    "ignored_roles": [],
    # If the bot should log all actions in the server.
    "guild_logs_enabled": False,
    "guild_log_channel": None,  # The channel to log actions in.
    # If the bot should send the news about major updates to the server.
    "bot_updates_on": False,
    # The channel to send the news about major updates to.
    "bot_updates_channel": None
}
