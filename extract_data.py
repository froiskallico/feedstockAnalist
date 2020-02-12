import pandas as pd
from database import Database
import csv

class App(object):
  def __init__(self):
    self.db = Database()
    op = self.get_op()

    self.OSE(op)
    self.ISE(op)
    self.chicotes()
    self.fic_tec()
    self.mps()
    self.IPC()
    self.PCO()
    self.CADASTRO()
    self.mov_ite()


  def get_op(self):
    # return input("Digite o numero da OP: ")
    return 114562

  def listify_dataset(self, ds):
    return str(ds.to_list()).replace("[", "(").replace("]", ")")

  def OSE(self, op):
    self.ose = pd.read_sql(
      "SELECT * FROM ORDEMSER WHERE PK_OSE = {}".format(str(op)),
      self.db.connection
    )

    self.ose.to_csv('ORDEMSER.csv', sep=';', quoting=csv.QUOTE_NONNUMERIC)

  def ISE(self, op):
    self.ise = pd.read_sql(
      "SELECT * FROM ITE_OSE WHERE FK_OSE = {}".format(str(op)),
      self.db.connection
    )
    self.ise.to_csv('ITE_OSE.csv', sep=';', quoting=csv.QUOTE_NONNUMERIC)

  def chicotes(self):
    self.chicotes = pd.read_sql(
      "SELECT * FROM PRODUTOS WHERE PK_PRO IN {}".format(self.listify_dataset(self.ise["FK_PRO"])),
      self.db.connection
    )

    self.chicotes.to_csv('CHICOTES.csv', sep=';', quoting=csv.QUOTE_NONNUMERIC)

  def fic_tec(self):
    self.fic_tec = pd.read_sql(
      "SELECT * FROM FIC_TEC WHERE FK_PROACAB IN {}".format(self.listify_dataset(self.chicotes["PK_PRO"])),
      self.db.connection
    )

    self.fic_tec.to_csv("FIC_TEC.csv", sep=';', quoting=csv.QUOTE_NONNUMERIC)

  def mps(self):
    self.mps = pd.read_sql(
      "SELECT * FROM PRODUTOS WHERE PK_PRO IN {}".format(self.listify_dataset(self.fic_tec["FK_PRO"])),
      self.db.connection
    )

    self.mps.to_csv("MPS.csv", sep=';', quoting=csv.QUOTE_NONNUMERIC)

    self.niveis_servico()

  def niveis_servico(self):
    self.niv_serv = pd.read_sql(
      "SELECT * FROM NIVEL_SERVICO",
      self.db.connection
    )

    self.niv_serv.to_csv("NIVEL_SERVICO.csv", sep=';', quoting=csv.QUOTE_NONNUMERIC)

  def IPC(self):
    self.ipc = pd.read_sql(
      "SELECT * FROM ITE_PCO WHERE FK_PRO IN {}".format(self.listify_dataset(self.mps["PK_PRO"])),
      self.db.connection
    )

    self.ipc.to_csv("IPC.csv", sep=';', quoting=csv.QUOTE_NONNUMERIC)

  def PCO(self):
    self.pco = pd.read_sql(
      "SELECT * FROM PEDCOMPR WHERE DATA >= '01.01.2018'",
      self.db.connection
    )

    self.pco.to_csv("PCO.csv", sep=';', quoting=csv.QUOTE_NONNUMERIC)

  def CADASTRO(self):
    self.cadastro = pd.read_sql(
      "SELECT * FROM CADASTRO WHERE PK_CAD IN (SELECT FK_CAD FROM PEDCOMPR WHERE DATA >= '01.01.2018')",
      self.db.connection
    )

    self.cadastro.to_csv("CADASTRO.csv", sep=';', quoting=csv.QUOTE_NONNUMERIC)

  def mov_ite(self):
    self.mov = pd.read_sql(
      """
        SELECT
            DOC.DATAEXP DATA,
            ITE.FK_PRO,
            SUM(ITE.QUANTIDADE) QUANTIDADE
        FROM
            MOV_ITEM ITE
            JOIN MOV_DOC DOC ON DOC.PK_DOC = ITE.FK_DOC

        WHERE
            DOC.DATAEXP >= '01.01.2019'
            AND DOC.DATAEXP <= CURRENT_TIMESTAMP
            AND DOC.SOMDIMEST='D' AND DOC.FK_TIP=6


        GROUP BY
            DOC.DATAEXP,
            ITE.FK_PRO
      """,
      self.db.connection
    )

    self.mov.to_csv("MOV.csv", sep=';', quoting=csv.QUOTE_NONNUMERIC)



App()