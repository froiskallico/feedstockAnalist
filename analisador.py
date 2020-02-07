from database import Database
from pprint import pprint
import numpy as np
import pandas as pd

class Analisador(object):
  def __init__(self, testMode=False):
    if testMode:
      self.get_op_dataset(testMode=testMode)
    else:
      op = input("Digite nr da OP para Análise: ")
      get_op_dataset(op_number=op)

  
  def get_op_dataset(self, op_number=None, testMode=False):
    if testMode:
      self.dataset = pd.read_csv('./test114486.csv', sep=';')
    else:
      self.dataset = pd.read_sql(
        "SELECT * FROM ANALISE_OP({})".format(str(op)),
        Database().connection
      )

    pprint(self.dataset)

    self.get_op_feedstock()

  def get_op_feedstock(self):
    pprint(self.dataset["CPD"])


    # dataset.to_csv('./test114486.csv', sep=';')



    
Analisador(testMode=True)