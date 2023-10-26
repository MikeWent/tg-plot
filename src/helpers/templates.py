from fastapi.templating import Jinja2Templates

from helpers.flash import get_flashed_messages
from helpers.settings import settings

templates = Jinja2Templates(directory="templates")
templates.env.globals["settings"] = settings
templates.env.globals["get_flashed_messages"] = get_flashed_messages
