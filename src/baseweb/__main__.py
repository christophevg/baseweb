import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from clevis import get_config
from gunicorn.app.wsgiapp import WSGIApplication


@dataclass
class GunicornConfig:
  bind         : str = "0.0.0.0:8000"
  workers      : int = 1
  worker_class : str = "uvicorn.workers.UvicornWorker"

@dataclass
class BasewebConfig:
  app_uri  : str = "app:asgi_app"
  gunicorn : GunicornConfig = field(default_factory=GunicornConfig)


class StandaloneApplication(WSGIApplication):
  def __init__(self, app_uri, options=None):
    self.options = options or {}
    self.app_uri = app_uri
    super().__init__()

  def load_config(self):
    config = {
      key: value
      for key, value in self.options.items()
      if key in self.cfg.settings and value is not None
    }
    for key, value in config.items():
      self.cfg.set(key.lower(), value)

def run():
  # add the current working folder to the system path for finding "local" modules
  sys.path.append(str(Path().resolve()))

  config = get_config(BasewebConfig, name="baseweb")
  StandaloneApplication(config.app_uri, asdict(config.gunicorn)).run()

if __name__ == "__main__":
  run()
