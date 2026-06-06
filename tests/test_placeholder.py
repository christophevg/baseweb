from baseweb import Baseweb
from baseweb.config import BasewebConfig


def test_placeholder():
  config = BasewebConfig(name="test")
  test = Baseweb(config)
  assert test._config.name == "test"
