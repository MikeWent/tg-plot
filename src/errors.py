class TelegramNotAuthorized(Exception):
    text = "Login into Telegram first"
    pass


class SettingsAreEmpty(Exception):
    text = "Update Telegram settings"
    pass
