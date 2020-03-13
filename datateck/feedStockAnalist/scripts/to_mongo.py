from pymongo import MongoClient
from app import App

a = App()

a.analyze(False, 114565)

report = a.report
print(report)
