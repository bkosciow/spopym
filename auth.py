from service.spotify import Spotify
from service.config import Config

cfg = Config()
spotify = Spotify(cfg)

print(spotify.spotify.me())
