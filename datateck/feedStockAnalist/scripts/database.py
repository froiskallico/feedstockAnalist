from pathlib import Path
import fdb
import os
import json

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if DEBUG:
    config_file_path = './config.json'
else:
    config_file_path = '/etc/config.json'

with open(config_file_path) as config_file:
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
