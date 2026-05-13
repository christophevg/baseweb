"""Shared pytest fixtures for baseweb tests."""

import pytest


@pytest.fixture
def app():
  """Create a test Baseweb app instance."""
  from baseweb import Baseweb

  app = Baseweb(__name__)
  app.config["TESTING"] = True
  return app


@pytest.fixture
def client(app):
  """Create a test client for the app."""
  return app.test_client()
