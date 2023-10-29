class TelegramNotAuthorized(Exception):
    text = "Login into Telegram first"
    pass


class SettingsAreEmpty(Exception):
    text = "Set Telegram & Channel settings"
    pass
