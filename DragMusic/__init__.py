from DragMusic.core.bot import Drag
from DragMusic.core.dir import dirr
from DragMusic.core.git import git
from DragMusic.core.userbot import Userbot
from DragMusic.misc import dbb, heroku

from .logging import LOGGER

dirr()
#git()
dbb()
heroku()

app = Drag()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

