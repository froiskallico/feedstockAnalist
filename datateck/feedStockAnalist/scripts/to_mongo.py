#%%
from app import App

a = App()

a.analyze(False, 114969)

report = a.report

#%%
from pymongo import MongoClient

mongodb_host = 'mongodb+srv://datateck:Data2803@datateck0-yjact.mongodb.net/feedStockAnalist?retryWrites=true',

client = MongoClient(mongodb_host)

db = client["TEST"]

# %%
import json
from datetime import datetime

def myconverter(o):
            if isinstance(o, datetime):
                return o.__str__()

document = json.dumps(report, default=myconverter)


#%%

db['testJson'].insert_one(a.report)



# %%
a.report.keys()

# %%
