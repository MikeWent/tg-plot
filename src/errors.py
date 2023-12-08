class BaseAppException(Exception):
    text: str
    redirect_to: str


class TelegramNotAuthorized(BaseAppException):
    text = "Login into Telegram first"
    redirect_to = "/telegram"


class SettingsAreEmpty(BaseAppException):
    text = "Set Telegram & Channel settings"
    redirect_to = "/settings"
