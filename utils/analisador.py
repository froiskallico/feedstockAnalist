from database import Database
from pprint import pprint
import numpy as np
import pandas as pd

class Analisador(object):
  def __init__(self, testMode=False, csvMode=False):
    if testMode:
      self.db = Database(testMode=testMode)
      self.get_op_dataset(csvMode=csvMode)
    else:
      op = input("Digite nr da OP para Análise: ")
      self.get_op_dataset(op_number=op)


  def get_op_dataset(self, op_number=None, testMode=False, csvMode=False):
    if csvMode:
      self.dataset = pd.read_csv('./test114486.csv', sep=';')
    else:
      self.dataset = pd.read_sql(
        "SELECT * FROM ANALISE_OP({})".format(str(op_number)),
        self.db.connection
      )



    self.get_op_feedstock()

  def get_op_feedstock(self):
    self.pds = self.dataset.iloc[:,1].to_list()


    pprint("SELECT RAZAO_SOCIAL FROM PRODUTOS WHERE PK_PRO IN {}".format(str(self.pds).replace('[', '(').replace(']', ')')))


    # dataset.to_csv('./test114486.csv', sep=';')




