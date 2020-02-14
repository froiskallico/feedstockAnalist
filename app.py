from database import Database
from pprint import pprint
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class App(object):
    def __init__(self):
        self.db = Database()
        self.get_op()
        # # self.get_ops_em_analise()
        # # self.get_chicotes_em_analise()
        # self.get_mps_em_analise()
        # # self.get_fic_tec()
        self.get_ocs_pendentes()
        self.get_ops_pendentes()

        # self.what_the_print()

    def get_op(self):
        self.lista_ops = str((114562))

    def listify_dataset(self, ds):
        return str(ds.to_list()).replace("[", "(").replace("]", ")")

    def get_ops_em_analise(self):
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

    def get_fic_tec(self):
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
        print("MP")
        pprint(self.mp_em_analise)
        pprint('-' * 120)
        # print("FIC_TEC")
        # pprint(self.fic_tec)
        # pprint('-' * 120)
        print("OCS")
        pprint(self.ocs_pendentes)
        pprint('-' * 120)
        print("OPS")
        pprint(self.ops_pendentes)
        pprint('-' * 120)

    def timeline(self):
        self.datas = pd.DataFrame({"ENTREGA": pd.date_range(pd.datetime.today().strftime('%Y-%m-%d'), periods= 10)})

        # self.timeline = pd.merge(self.datas, self.ocs_pendentes[self.ocs_penentes["CPD_MP"] == 1062]["CPD_MP", "ENTREGA", "QTD_PENDENTE_OC"], on="ENTREGA", how='outer', sort="ENTREGA").merge(self.ops_pendentes[["CPD_MP", "ENTREGA", "COMPROMETIDO"]], 'outer', ["ENTREGA", "CPD_MP"])
        ocs = self.ocs_pendentes[self.ocs_pendentes["CPD_MP"] == 1062][["CPD_MP", "ENTREGA", "QTD_PENDENTE_OC"]]
        ops = self.ops_pendentes[self.ops_pendentes["CPD_MP"] == 1062][["CPD_MP", "ENTREGA", "COMPROMETIDO"]]

        # TODO here merge the OCS_PENDENTES and OPS_PENDENTES dataframe and calculate BALANCE for each day
        # TODO Make it a "balance calculation function"
        # TODO run this "balance calculation function" for each "MP em analise"


        # print(ocs)
        print('-'*120)
        print(ops.to_string())




App().timeline()
