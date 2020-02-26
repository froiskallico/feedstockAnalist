# %%
from pprint import pprint
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from functools import reduce

# %%
class App(object):

    def __init__(self, csv=False):
        self.csv = csv
        self.path_csv = './csv/'

        # Instancia as variávies e data frames para rodar a análise

        # Se iniciar o App em movo CSV não cria conexão com Banco de Dados
        if not self.csv:
            from database import Database
            self.db = Database()
            self.get_op()

        self.get_ops_em_analise()
        self.get_chicotes_em_analise()
        self.get_mps_em_analise()
        # self.get_fic_tec()
        self.get_ocs_pendentes()
        self.get_ops_pendentes()

        # self.what_the_print()

        self.timeline()

    def get_op(self):
        # Define o numero da(s) OPS(s) a ser(em) analisada(s)
        self.lista_ops = str((114562))

    def get_ops_em_analise(self):
        # ANALISE
        # |-OPS

        # Busca do Banco de Dados de Origem as OPs para analise
        def sql():
            return pd.read_sql(
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

        # Busca do arqiuvo CSV
        def csv():
            return pd.read_csv(self.path_csv + 'ops_em_analise.csv')

        self.ops_em_analise = csv() if self.csv else sql()

    def get_chicotes_em_analise(self):
        # Obtém a lista de chicotes vinculados às OPs que estão sendo analisadas
        #
        # ANALISE
        # |-OPS
        #   |-CHICOTES
        #

        def sql():
            return pd.read_sql(
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

        def csv():
            return pd.read_csv(self.path_csv + "chicotes_em_analise.csv")

        self.chicotes_em_analise = csv() if self.csv else sql()

    def get_mps_em_analise(self):
        # Obtém a lista de Matérias Primas vinculadas aos chicotes em análise
        #
        # ANALISE
        # |-OPS
        #   |-CHICOTES
        #     |-MATERIAS PRIMAS
        #

        def sql():
            return pd.read_sql(
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

        def csv():
            return pd.read_csv(self.path_csv + 'mp_em_analise.csv')

        self.mp_em_analise = csv() if self.csv else sql()

        # Normaliza os percentuais a considerar dos estoques LP e Corte
        self.mp_em_analise = self.mp_em_analise.fillna(
            value={"PERC_ESTOQUE_LP": 50}).replace({'PERC_ESTOQUE_LP': 0}, 50)
        self.mp_em_analise = self.mp_em_analise.fillna(
            value={"PERC_ESTOQUE_CORTE": 50}).replace({'PERC_ESTOQUE_CORTE': 0}, 50)

        # Aplica os percentuais a considerar em cada estoque (LP/Corte)
        self.mp_em_analise["ESTOQUE_LP_CONSIDERADO"] = self.mp_em_analise["ESTOQUE_LP"] * (
            self.mp_em_analise["PERC_ESTOQUE_LP"]/100)
        self.mp_em_analise["ESTOQUE_CORTE_CONSIDERADO"] = self.mp_em_analise["ESTOQUE_CORTE"] * (
            self.mp_em_analise["PERC_ESTOQUE_CORTE"]/100)

        # Calcula o saldo inicial das matérias primas
        estoques = (
            "ESTOQUE",
            "ESTOQUE_LP_CONSIDERADO",
            "ESTOQUE_CORTE_CONSIDERADO"
        )
        self.mp_em_analise["SALDO_INICIAL"] = sum(
            [self.mp_em_analise[campo] for campo in estoques])

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
        def sql():
            return pd.read_sql(
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

        def csv():
            return pd.read_csv(self.path_csv + 'ocs_pendentes.csv')

        self.ocs_pendentes = csv() if self.csv else sql()

        # Normliza as datas para formato DateTime
        self.ocs_pendentes["ENTREGA"] = pd.to_datetime(self.ocs_pendentes["ENTREGA"])

    def get_ops_pendentes(self):
        # Obtem as ordens de produção pendentes para as MPs vinculadas à analise
        def sql():
            return pd.read_sql(
                # TODO: HERE in the SQL Query take the last day of "Semana" where ise_geral.entrega and ipe.entrega is null
                """
                SELECT DISTINCT
                    FIC_GERAL.FK_PRO CPD_MP,
                    FIC_GERAL.FK_PROACAB CPD_CHICOTE,
                    CHICOTE.COD_FABRIC CODIGO_CHICOTE,
                    COALESCE(ISE_GERAL.ENTREGA, IPE.ENTREGA) ENTREGA,
                    COALESCE(ISE_GERAL.SEMANA, IPE.SEM_ENTREG) SEMANA_ENTREGA,
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

        def csv():
            return pd.read_csv(self.path_csv + 'ops_pendentes.csv')

        self.ops_pendentes = csv() if self.csv else sql()

        # Normliza as datas para formato DateTime
        self.ops_pendentes["ENTREGA"] = pd.to_datetime(self.ops_pendentes["ENTREGA"])

        # TODO: COMMENT CODE BELOW
        self.ops_sem_data_com_semana = self.ops_pendentes[self.ops_pendentes["ENTREGA"].isna()]
        self.ops_sem_data_com_semana["NSEM"] = self.ops_sem_data_com_semana["SEMANA_ENTREGA"].str.slice(0, 2).astype(int)
        self.ops_sem_data_com_semana["NANO"] = self.ops_sem_data_com_semana["SEMANA_ENTREGA"].str.slice(2).astype(int)
        self.ops_sem_data_com_semana["FDOY"] = pd.to_datetime(dict(year=self.ops_sem_data_com_semana["NANO"], month=1, day=1))
        self.ops_sem_data_com_semana["FDOYWD"] = self.ops_sem_data_com_semana["FDOY"].dt.weekday
        self.ops_sem_data_com_semana["ENTREGA_NOVA"] = self.ops_sem_data_com_semana["FDOY"] + pd.to_timedelta(self.ops_sem_data_com_semana["NSEM"] * 7 - 3 - self.ops_sem_data_com_semana["FDOYWD"], 'D')
        self.ops_sem_data_com_semana = self.ops_sem_data_com_semana["ENTREGA"].fillna(self.ops_sem_data_com_semana["ENTREGA_NOVA"])

        self.ops_pendentes["ENTREGA"] = self.ops_pendentes["ENTREGA"].fillna(self.ops_sem_data_com_semana)







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
        pass

    def timeline(self, CPD_MP=800):
        # Define o horizonte de programação para o item em análise
        horizonte_programacao = self.mp_em_analise.loc[self.mp_em_analise["CPD_MP"]
                                                    == CPD_MP]["HORIZONTE_PROGRAMACAO"].iloc[0] * 7

        # Cria DataSeries com as todas as datas existentes
        # entre hoje e o limite do horizonte de programação
        self.datas = pd.DataFrame(
            {
                "ENTREGA":
                pd.date_range(
                    pd.datetime.today().strftime('%Y-%m-%d'),
                    periods=horizonte_programacao
                )
            }
        )

        # Busca as OCs somente do CPD em analise e soma as quantidades pendentes das ocs agrupando por data.
        ocs = self.ocs_pendentes.loc[self.ocs_pendentes["CPD_MP"] == CPD_MP][[
            "CPD_MP", "ENTREGA", "QTD_PENDENTE_OC"]].groupby(["CPD_MP", "ENTREGA"]).sum().reset_index()
        # Busca as OPs somente do CPD em analise e soma as quantidades pendentes das ops agrupando por data.
        ops = self.ops_pendentes[self.ops_pendentes["CPD_MP"] == CPD_MP][[
            "CPD_MP", "ENTREGA", "COMPROMETIDO"]].groupby(["CPD_MP", "ENTREGA"]).sum().reset_index()

        # Define um array com os DataFrames que serão mesclados
        dfs_to_merge = [self.datas, ocs, ops]

        # Mescla os DataFrames instanciando a timeline do item no objeto self.tl
        self.tl = reduce(lambda left, right: pd.merge(
            left, right, how="left", sort="ENTREGA").fillna({ "CPD_MP": CPD_MP }), dfs_to_merge)

        # Normaliza as quantidades pendentes para ZERO onde forem NaN
        self.tl = self.tl.fillna({ "QTD_PENDENTE_OC": 0, "COMPROMETIDO": 0 })

        # Insere coluna no DataFrame self.tl
        self.tl["SALDO_INICIAL"] = 0
        self.tl["SALDO_FINAL"] = 0

        # Define o saldo inicial da primeira data no self.tl
        self.tl.loc[0, "SALDO_INICIAL"] = self.mp_em_analise.loc[self.mp_em_analise["CPD_MP"] == CPD_MP, "SALDO_INICIAL"].to_numpy()


        # Define o saldo final da primeira data no self.tl
        self.tl.loc[0, "SALDO_FINAL"] = self.tl.loc[0, "SALDO_INICIAL"] - self.tl.loc[0, "COMPROMETIDO"] + self.tl.loc[0, "QTD_PENDENTE_OC"]

        # Calcula os saldos final e inicial para as demais linhas no self.tl
        for l in range(1, self.tl.size):
            self.tl.loc[l, "SALDO_INICIAL"] = self.tl.loc[l-1, "SALDO_FINAL"]
            self.tl.loc[l, "SALDO_FINAL"] = self.tl.loc[l, "SALDO_INICIAL"] - self.tl.loc[l, "COMPROMETIDO"] + self.tl.loc[l, "QTD_PENDENTE_OC"]

        # Cria a coluna que indica SE e QUANDO ira faltar MP na self.tl
        self.tl["FALTA"] = self.tl["SALDO_FINAL"] <= 0

        # Define as datas em que haverá falta de MP
        self.datas_falta = self.tl[self.tl["FALTA"]][["ENTREGA", "CPD_MP"]]

        # self.ops_falta =  ops.loc[ops["ENTREGA"] >= self.datas_falta["ENTREGA"].min()]
        pri_data_falta = self.datas_falta["ENTREGA"].min()

        self.ops_falta = self.ops_pendentes[self.ops_pendentes["CPD_MP"]==800].set_index("ENTREGA")[:pri_data_falta]

        # TODO: Get a subset from self.ops_pendentes filtering where "ENTREGA" in self.datas_falta and store it to self.ops_falta
        # TODO: Save self.ops_falta to HTML with to_html() method.

        # TODO: Execute the timeline method to all self.mp_em_analise itens

a = App(csv=True)


# %%
