import argparse
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import tomllib
from clevis import configclass, get_cmd, get_config, get_factory
from gunicorn.app.wsgiapp import WSGIApplication


@dataclass
class GunicornConfig:
  bind         : str = "0.0.0.0:8000"
  workers      : int = 1
  worker_class : str = "uvicorn.workers.UvicornWorker"

@configclass(cmd="serve")
class BasewebServeConfig:
  app_uri  : str = "app:asgi_app"
  gunicorn : GunicornConfig = field(default_factory=GunicornConfig)

@configclass(cmd="config")
class BasewebConfigConfig:
  pass

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

def serve():
  # add the current working folder to the system path for finding "local" modules
  sys.path.append(str(Path().resolve()))

  config = get_config(BasewebServeConfig, name="baseweb")

  StandaloneApplication(config.app_uri, asdict(config.gunicorn)).run()

def config():
  config = BasewebServeConfig()
  Path("baseweb.toml").write_text(f"""# default baseweb configuration
app_uri = "{config.app_uri}"

[gunicorn]
bind = "{config.gunicorn.bind}"
workers = {config.gunicorn.workers}
worker_class = "{config.gunicorn.worker_class}"
""")
  print("create baseweb.toml")

def run():
  {
    "serve" : serve,
    "config": config
  }[get_cmd()]()

if __name__ == "__main__":
  run()
