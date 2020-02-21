#%%
from database import Database
from pprint import pprint
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from functools import reduce

#%%
class App(object):
    def __init__(self):
        # Instancia as variávies e data frames para rodar a análise
        self.db = Database()
        self.get_op()
        # # self.get_ops_em_analise()
        # # self.get_chicotes_em_analise()
        self.get_mps_em_analise()
        # # self.get_fic_tec()
        # self.get_ocs_pendentes()
        # self.get_ops_pendentes()

        # self.what_the_print()

        # self.timeline()

    def get_op(self):
        # Define o numero da(s) OPS(s) a ser(em) analisada(s)
        self.lista_ops = str((114562))

    def get_ops_em_analise(self):
        # Busca do Banco de Dados de Origem as OPs para analise
        #
        # ANALISE
        # |-OPS

        self.ops_em_analise = pd.read_sql(
            """
                SELECT
                    OSE.PK_OSE OP,
                    OSE.DATA,
                    CAD.RAZAO_SOCIAL,
                    PED.PK_PED

                FROM
                    ORDEMSER OSE
                    JOIN ITE_OSE ISE ON ISE.FK_OSE = OSE.PK_OSE
                    JOIN ITE_PED IPE ON IPE.PK_IPE = ISE.fk_ipe
                    JOIN PEDIDOS PED ON PED.PK_PED = IPE.FK_PED
                    JOIN CADASTRO CAD ON CAD.PK_CAD = PED.fk_cad

                WHERE
                    OSE.PK_OSE IN ({})
            """.format(str(self.lista_ops)),
            self.db.connection)

    def get_chicotes_em_analise(self):
        # Obtém a lista de chicotes vinculados às OPs que estão sendo analisadas
        #
        # ANALISE
        # |-OPS
        #   |-CHICOTES
        #

        self.chicotes_em_analise = pd.read_sql(
            """
                SELECT
                    OSE.PK_OSE OP,
                    ISE.FK_PRO CPD_CHICOTE,
                    CHICOTE.COD_FABRIC CODIGO_CHICOTE,
                    CHICOTE.DESC_COMPL DESCRICAO_CHICOTE,
                    ISE.QUANTIDADE QTD_TOTAL,
                    ISE.QUANTIDADE - COALESCE(ISE.QTD_CANC, 0) - COALESCE(ISE.QTD_PROD, 0) QTD_PENDENTE,
                    COALESCE(ISE.ENTREGA, IPE.ENTREGA) ENTREGA

                FROM
                    ORDEMSER OSE
                    JOIN ITE_OSE ISE ON ISE.FK_OSE = OSE.PK_OSE
                    JOIN ITE_PED IPE ON IPE.PK_IPE = ISE.FK_IPE
                    JOIN PRODUTOS CHICOTE ON CHICOTE.PK_PRO = ISE.FK_PRO

                WHERE
                    OSE.PK_OSE IN ({})
            """.format(self.lista_ops),
            self.db.connection
        )

    def get_mps_em_analise(self):
        # Obtém a lista de Matérias Primas vinculadas aos chicotes em análise
        #
        # ANALISE
        # |-OPS
        #   |-CHICOTES
        #     |-MATERIAS PRIMAS
        #

        self.mp_em_analise = pd.read_sql(
            """
                SELECT DISTINCT
                    MP.PK_PRO CPD_MP,
                    MP.COD_FABRIC CODIGO_MP,
                    MP.DESC_COMPL DESCRICAO_MP,
                    (SELECT DESCRICAO FROM SUBGRUPOS WHERE PK_SGR = MP.FK_SGR) SUBGRUPO,
                    COALESCE(MP.QUANTIDADE, 0) ESTOQUE,
                    COALESCE(MP.QTD_LINHA, 0) ESTOQUE_LP,
                    COALESCE(MP.QTD_CORTE, 0) ESTOQUE_CORTE,
                    COALESCE(MP.PERC_ESTOQUE_LP, 0) PERC_ESTOQUE_LP,
                    COALESCE(MP.PERC_ESTOQUE_CORTE, 0) PERC_ESTOQUE_CORTE,
                    MP.HORIZONTE_PROGRAMACAO

                FROM
                    FIC_TEC FIC
                    JOIN PRODUTOS MP ON MP.PK_PRO = FIC.FK_PRO
                    JOIN ITE_OSE ISE ON ISE.FK_PRO = FIC.FK_PROACAB

                WHERE
                    ISE.FK_OSE IN ({})
            """.format(self.lista_ops),
            self.db.connection
        )

        # Normaliza os percentuais a considerar dos estoques LP e Corte
        self.mp_em_analise = self.mp_em_analise.fillna(value={"PERC_ESTOQUE_LP": 50}).replace({'PERC_ESTOQUE_LP': 0}, 50)
        self.mp_em_analise = self.mp_em_analise.fillna(value={"PERC_ESTOQUE_CORTE": 50}).replace({'PERC_ESTOQUE_CORTE': 0}, 50)

        # Aplica os percentuais a considerar em cada estoque (LP/Corte)
        self.mp_em_analise["ESTOQUE_LP_CONSIDERADO"] = self.mp_em_analise["ESTOQUE_LP"] * (self.mp_em_analise["PERC_ESTOQUE_LP"]/100)
        self.mp_em_analise["ESTOQUE_CORTE_CONSIDERADO"] = self.mp_em_analise["ESTOQUE_CORTE"] * (self.mp_em_analise["PERC_ESTOQUE_CORTE"]/100)

        # Calcula o saldo inicial das matérias primas
        estoques = ("ESTOQUE", "ESTOQUE_LP_CONSIDERADO", "ESTOQUE_CORTE_CONSIDERADO")
        self.mp_em_analise["SALDO_INICIAL"] = sum([self.mp_em_analise[campo] for campo in estoques])

    def get_fic_tec(self):
        # Obtém as fichas técnicas dos chicotes vinculados às OPs em análise
        self.fic_tec = pd.read_sql(
            """
                SELECT
                    FIC.FK_PROACAB CPD_CHICOTE,
                    MP.PK_PRO CPD_MP,
                    SUM(FIC.QUANTIDADE)

                FROM
                    FIC_TEC FIC
                    JOIN PRODUTOS MP ON MP.PK_PRO = FIC.FK_PRO
                    JOIN SUBGRUPOS SGR ON SGR.PK_SGR = MP.FK_SGR
                    JOIN ITE_OSE ISE ON ISE.FK_PRO = FIC.FK_PROACAB

                WHERE
                    ISE.FK_OSE IN ({})

                GROUP BY
                    CPD_CHICOTE,
                    CPD_MP
            """.format(self.lista_ops),
            self.db.connection
        )

    def get_ocs_pendentes(self):
        # Obtem as ordens de compras pendentes para as MPs vinculadas à analise
        self.ocs_pendentes = pd.read_sql(
            """
                SELECT DISTINCT
                    IPC.FK_PRO CPD_MP,
                    PCO.PK_PCO OC,
                    CAD.RAZAO_SOCIAL FORNECEDOR,
                    IPC.QUANTIDADE - COALESCE(IPC.QTD_RECEB, 0) - COALESCE(IPC.QTD_CANC, 0) QTD_PENDENTE_OC,
                    IPC.ENTREGA,
                    MOE.SIMBOLO,
                    (IPC.QUANTIDADE - COALESCE(IPC.QTD_RECEB, 0) - COALESCE(IPC.QTD_CANC, 0)) * IPC.VALOR VALOR_TOTAL

                FROM
                    ITE_PCO IPC
                    JOIN PEDCOMPR PCO ON PCO.pk_pco = IPC.FK_PCO
                    JOIN CADASTRO CAD ON CAD.PK_CAD = PCO.FK_CAD
                    JOIN MOEDAS MOE ON MOE.PK_MOE = IPC.FK_MOE
                    JOIN FIC_TEC FIC ON FIC.FK_PRO = IPC.FK_PRO
                    JOIN ITE_OSE ISE ON ISE.FK_PRO = FIC.FK_PROACAB

                WHERE
                    IPC.QUANTIDADE - COALESCE(IPC.QTD_RECEB, 0) - COALESCE(IPC.QTD_CANC, 0) > 0 AND
                    ISE.FK_OSE IN ({})
            """.format(self.lista_ops),
            self.db.connection
        )

    def get_ops_pendentes(self):
        # Obtem as ordens de produção pendentes para as MPs vinculadas à analise
        self.ops_pendentes = pd.read_sql(
            # TODO: HERE in the SQL Query take the last day of "Semana" where ise_geral.entrega and ipe.entrega is null
            """
                SELECT DISTINCT
                    FIC_GERAL.FK_PRO CPD_MP,
                    FIC_GERAL.FK_PROACAB CPD_CHICOTE,
                    CHICOTE.COD_FABRIC CODIGO_CHICOTE,
                    COALESCE(ISE_GERAL.ENTREGA, IPE.ENTREGA) ENTREGA,
                    ISE_GERAL.FK_OSE OP,
                    CAD.RAZAO_SOCIAL CLIENTE,
                    (ISE_GERAL.QUANTIDADE - COALESCE(ISE_GERAL.QTD_CANC, 0) - COALESCE(ISE_GERAL.QTD_PROD, 0)) * FIC_GERAL.QUANTIDADE COMPROMETIDO

                FROM
                    FIC_TEC FIC_OP
                    JOIN FIC_TEC FIC_GERAL ON FIC_GERAL.FK_PRO = FIC_OP.FK_PRO
                    JOIN ITE_OSE ISE_OP ON ISE_OP.FK_PRO = FIC_OP.FK_PROACAB
                    JOIN ITE_OSE ISE_GERAL ON ISE_GERAL.FK_PRO = FIC_GERAL.FK_PROACAB
                    JOIN ITE_PED IPE ON IPE.PK_IPE = ISE_GERAL.FK_IPE
                    JOIN PRODUTOS CHICOTE ON CHICOTE.PK_PRO = FIC_GERAL.FK_PROACAB
                    JOIN PEDIDOS PED ON PED.PK_PED = IPE.FK_PED
                    JOIN CADASTRO CAD ON CAD.PK_CAD = PED.FK_CAD

                WHERE
                    ISE_GERAL.QUANTIDADE - COALESCE(ISE_GERAL.QTD_CANC, 0) - COALESCE(ISE_GERAL.QTD_PROD, 0) > 0 AND
                    ISE_OP.FK_OSE IN ({})
        """.format(self.lista_ops),
            self.db.connection
        )

    def what_the_print(self):
        # print("OPS")
        # pprint(self.ops_em_analise)
        # pprint('-' * 120)
        # print("CHICOTES")
        # pprint(self.chicotes_em_analise)
        # pprint('-' * 120)
        # print("MP")
        # pprint(self.mp_em_analise)
        # pprint('-' * 120)
        # # print("FIC_TEC")
        # # pprint(self.fic_tec)
        # # pprint('-' * 120)
        # print("OCS")
        # pprint(self.ocs_pendentes)
        # pprint('-' * 120)
        # print("OPS")
        # pprint(self.ops_pendentes)
        # pprint('-' * 120)

#%%
a = App()

#%%
def timeline(self, CPD_MP=1062):
    self.horizonte_programacao = self.mp_em_analise.loc[0]

    self.datas = pd.DataFrame({"ENTREGA": pd.date_range(
        pd.datetime.today().strftime('%Y-%m-%d'), periods=10)})



    ocs = self.ocs_pendentes[self.ocs_pendentes["CPD_MP"] == CPD_MP][["CPD_MP", "ENTREGA", "QTD_PENDENTE_OC"]].groupby(["CPD_MP", "ENTREGA"]).sum()
    ops = self.ops_pendentes[self.ops_pendentes["CPD_MP"] == CPD_MP][["CPD_MP", "ENTREGA", "COMPROMETIDO"]].groupby(["CPD_MP", "ENTREGA"]).sum()

    dfs_to_merge = [self.datas, ocs, ops]

    # # TODO here merge the OCS_PENDENTES and OPS_PENDENTES dataframe and calculate BALANCE for each day
    self.tl = reduce(lambda left, right: pd.merge(left, right, on="ENTREGA", how="outer", sort="ENTREGA"), dfs_to_merge)

    estoques = [self.mp_em_analise[self.mp_em_analise["CPD_MP"] == CPD_MP][campo]
                          for campo in ("ESTOQUE", "ESTOQUE_LP_CONSIDERADO", "ESTOQUE_CORTE_CONSIDERADO")]

    SALDO_INICIAL = reduce(lambda a, b: sum(a+b), estoques)

    self.tl.at[0, "SALDO_INICIAL"] = SALDO_INICIAL

    # print("timeline")

    pprint(self.tl.to_string())


    # TODO Make it a "balance calculation function"
    # TODO run this "balance calculation function" for each "MP em analise"



setattr(a, 'timeline', timeline)

a.timeline(a)


# %%
