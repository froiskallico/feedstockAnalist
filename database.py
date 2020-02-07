from pathlib import Path
from dotenv import load_dotenv
import fdb
import os

class Database(object):
  def __init__(self, testMode=False):
    if testMode:
      env_file = '.test.env'
    else:
      env_file = '.env'

    env_path = Path('.') / env_file
    load_dotenv(dotenv_path = env_path)

    self.connection =  fdb.connect(
      dsn=os.getenv("LEGACY_DATABASE_DSN"),
      user=os.getenv("LEGACY_DATABASE_USER"),
      password=os.getenv("LEGACY_DATABASE_PASSWORD"),
      charset=os.getenv("LEGACY_DATABASE_CHARSET")
    )

    self.cursor = self.connection.cursor()