from pathlib import Path
from dotenv import load_dotenv
import fdb
import os

import json

with open('/etc/config.json') as config_file:
    config = json.load(config_file)

class Database(object):
  def __init__(self, testMode=False):
    self.connection =  fdb.connect(
      dsn=config.get("LEGACY_DATABASE_DSN"),
      user=config.get("LEGACY_DATABASE_USER"),
      password=config.get("LEGACY_DATABASE_PASSWORD"),
      charset=config.get("LEGACY_DATABASE_CHARSET")
    )

    self.cursor = self.connection.cursor()
