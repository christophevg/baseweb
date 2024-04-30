from baseweb import Baseweb

def test_placeholder():
  test = Baseweb("test")
  assert test.name == "test"
