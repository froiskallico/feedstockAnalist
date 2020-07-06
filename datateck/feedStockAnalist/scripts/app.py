# %%
from pprint import pprint
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from functools import reduce
import json
from io import StringIO
import math

start_time = datetime.now()

pd.options.mode.chained_assignment = None


class App(object):
    def __init__(self):
        self.path_csv = '../../../../csv/'

    def get_list_of_items_to_analyze(self, read_from_csv=False, production_orders_to_analyze_list=None, analyze_radar_items=False):
        self.read_from_csv = read_from_csv
        self.production_orders_to_analyze_list = production_orders_to_analyze_list
        self.analyze_radar_items = analyze_radar_items

        # Se iniciar o App em movo CSV não cria conexão com Banco de Dados
        if not self.read_from_csv:
            try:
                from feedStockAnalist.scripts.database import Database
            except:
                from database import Database

            self.db = Database()

        if not self.analyze_radar_items:
            self.get_production_orders_to_analyze_list()
            self.get_production_orders_to_analyze()
            self.get_products_to_analyze()

        self.get_feedstock_to_analyze()
        self.get_open_purchase_orders()
        self.get_ops_pendentes()

        self.CPDs = self.feedstock_to_analyze["CPD_MP"]

        # for cpd in self.CPDs:
        #     self.timeline(CPD_MP=cpd)

        return self.CPDs.to_list()

    def get_production_orders_to_analyze_list(self):
        # Define o numero da(s) OPS(s) a ser(em) analisada(s)
        if not self.production_orders_to_analyze_list:
            self.production_orders_to_analyze_list = input(
                "Informe o numero da(s) op(s) para analisar: ")

        return self.production_orders_to_analyze_list

    def get_production_orders_to_analyze(self):
        # ANALISE
        # |-OPS

        def fetch_data_from_database():
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
                """.format(str(self.production_orders_to_analyze_list)),
                self.db.connection)

        def fetch_data_from_csv():
            return pd.read_csv(self.path_csv + 'ops_em_analise.csv')

        self.production_orders_to_analyze = fetch_data_from_csv(
        ) if self.read_from_csv else fetch_data_from_database()

        return self.production_orders_to_analyze

    def get_products_to_analyze(self):
        # Obtém a lista de chicotes vinculados às OPs que estão sendo analisadas
        #
        # ANALISE
        # |-OPS
        #   |-CHICOTES
        #

        def fetch_data_from_database():
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
            """.format(self.production_orders_to_analyze_list),
                self.db.connection
            )

        def fetch_data_from_csv():
            return pd.read_csv(self.path_csv + "produtos_em_analise.csv")

        self.products_to_analyze = fetch_data_from_csv(
        ) if self.read_from_csv else fetch_data_from_database()

        return self.products_to_analyze

    def get_feedstock_to_analyze(self):
        # Obtém a lista de Matérias Primas vinculadas aos chicotes em análise
        #
        # ANALISE
        # |-OPS
        #   |-CHICOTES
        #     |-MATERIAS PRIMAS
        #

        def fetch_data_from_database():
            if self.analyze_radar_items:
                query = """
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
                        MP.HORIZONTE_PROGRAMACAO,
                        MP.PREC_COMPR CUSTO_MP,
                        MOE.SIMBOLO SIMBOLO,
                        MP.MESES_CONSUMO_MRP,
                        MP.PERIODICIDADE,
                        MP.LEADTIME FES,
                        NIV.FATOR_SERVICO,
                        MP.MOQ,
                        MP.DELAY_OC LEADTIME

                    FROM
                        FIC_TEC FIC
                        JOIN PRODUTOS MP ON MP.PK_PRO = FIC.FK_PRO
                        JOIN RADAR_ITENS_CRITICOS RIC ON RIC.FK_PRO = FIC.FK_PROACAB
                        LEFT JOIN MOEDAS MOE ON MOE.PK_MOE = MP.FK_MOE
                        LEFT JOIN NIVEL_SERVICO NIV ON NIV.PK_NIV = MP.FK_NIV

                    WHERE
                        RIC.DATA_CONCLUSAO IS NULL
                """
            else:
                query = """
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
                        MP.HORIZONTE_PROGRAMACAO,
                        MP.PREC_COMPR CUSTO_MP,
                        MOE.SIMBOLO SIMBOLO,
                        MP.MESES_CONSUMO_MRP,
                        MP.PERIODICIDADE,
                        MP.LEADTIME FES,
                        NIV.FATOR_SERVICO,
                        MP.MOQ,
                        MP.DELAY_OC LEADTIME

                    FROM
                        FIC_TEC FIC
                        JOIN PRODUTOS MP ON MP.PK_PRO = FIC.FK_PRO
                        JOIN ITE_OSE ISE ON ISE.FK_PRO = FIC.FK_PROACAB
                        LEFT JOIN MOEDAS MOE ON MOE.PK_MOE = MP.FK_MOE
                        LEFT JOIN NIVEL_SERVICO NIV ON NIV.PK_NIV = MP.FK_NIV

                    WHERE
                        ISE.FK_OSE IN ({})
                """.format(self.production_orders_to_analyze_list)

            return pd.read_sql(query, self.db.connection)

        def fetch_data_from_csv():
            return pd.read_csv(self.path_csv + 'mp_em_analise.csv')

        self.feedstock_to_analyze = fetch_data_from_csv(
        ) if self.read_from_csv else fetch_data_from_database()

        def normalize_fields(dict_of_data_to_normalize):
            for key, value in dict_of_data_to_normalize.items():
                self.feedstock_to_analyze = self.feedstock_to_analyze.fillna(
                    value={key: value}).replace({key: 0}, value)

        def calculate_stocks_to_consider():
            self.feedstock_to_analyze["ESTOQUE_LP_CONSIDERADO"] = self.feedstock_to_analyze["ESTOQUE_LP"] * (
                self.feedstock_to_analyze["PERC_ESTOQUE_LP"]/100)
            self.feedstock_to_analyze["ESTOQUE_CORTE_CONSIDERADO"] = self.feedstock_to_analyze["ESTOQUE_CORTE"] * (
                self.feedstock_to_analyze["PERC_ESTOQUE_CORTE"]/100)

        def calculate_opening_balance():
            stocks = (
                "ESTOQUE",
                "ESTOQUE_LP_CONSIDERADO",
                "ESTOQUE_CORTE_CONSIDERADO"
            )

            self.feedstock_to_analyze["SALDO_INICIAL"] = sum(
                [self.feedstock_to_analyze[field] for field in stocks])

        data_to_normalize = {"PERC_ESTOQUE_LP": 50,
                             "PERC_ESTOQUE_CORTE": 50,
                             "HORIZONTE_PROGRAMACAO": 100,
                             "PERIODICIDADE": 1,
                             "FES": 20,
                             "FATOR_SERVICO": 2,
                             "MOQ": 1,
                             "LEADTIME": 2
                             }

        normalize_fields(data_to_normalize)
        calculate_stocks_to_consider()
        calculate_opening_balance()

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
            """.format(self.production_orders_to_analyze_list),
            self.db.connection
        )

    def get_open_purchase_orders(self):
        # Obtem as ordens de compras pendentes para as MPs vinculadas à analise
        def fetch_data_from_database():
            if self.analyze_radar_items:
                query = """
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
                        JOIN RADAR_ITENS_CRITICOS RIC ON RIC.FK_PRO = FIC.FK_PROACAB

                    WHERE
                        IPC.QUANTIDADE - COALESCE(IPC.QTD_RECEB, 0) - COALESCE(IPC.QTD_CANC, 0) > 0 AND
                        RIC.DATA_CONSLUSAO IS NULL
                """
            else:
                query = """
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
                """.format(self.production_orders_to_analyze_list)
            return pd.read_sql(
                query,
                self.db.connection
            )

        def fetch_data_from_csv():
            return pd.read_csv(self.path_csv + 'ocs_pendentes.csv')

        self.open_purchase_orders = fetch_data_from_csv(
        ) if self.read_from_csv else fetch_data_from_database()

        # Normliza as datas para formato DateTime
        self.open_purchase_orders["ENTREGA"] = pd.to_datetime(
            self.open_purchase_orders["ENTREGA"])

    def get_ops_pendentes(self):
        # Obtem as ordens de produção pendentes para as MPs vinculadas à analise
        def fetch_data_from_database():
            if self.analyze_radar_items:
                query = """
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
                        JOIN RADAR_ITENS_CRITICOS RIC ON RIC.FK_PRO = FIC_OP.FK_PROACAB
                        JOIN ITE_OSE ISE_GERAL ON ISE_GERAL.FK_PRO = FIC_GERAL.FK_PROACAB
                        JOIN ITE_PED IPE ON IPE.PK_IPE = ISE_GERAL.FK_IPE
                        JOIN PRODUTOS CHICOTE ON CHICOTE.PK_PRO = FIC_GERAL.FK_PROACAB
                        JOIN PEDIDOS PED ON PED.PK_PED = IPE.FK_PED
                        JOIN CADASTRO CAD ON CAD.PK_CAD = PED.FK_CAD

                    WHERE
                        ISE_GERAL.QUANTIDADE - COALESCE(ISE_GERAL.QTD_CANC, 0) - COALESCE(ISE_GERAL.QTD_PROD, 0) > 0 AND
                        RIC.DATA_CONCLUSAO IS NULL
                """
            else:
                query = """
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
                """.format(self.production_orders_to_analyze_list)

            return pd.read_sql(
                query,
                self.db.connection
            )

        def fetch_data_from_csv():
            return pd.read_csv(self.path_csv + 'ops_pendentes.csv', dtype={'SEMANA_ENTREGA': str})

        self.ops_pendentes = fetch_data_from_csv(
        ) if self.read_from_csv else fetch_data_from_database()

        # Normliza as datas para formato DateTime
        self.ops_pendentes["ENTREGA"] = pd.to_datetime(
            self.ops_pendentes["ENTREGA"])  # , dayfirst=True, format='%Y-%m-%d')

        self.ops_sem_data_com_semana = self.ops_pendentes[self.ops_pendentes["ENTREGA"].isna(
        )].dropna(subset=["SEMANA_ENTREGA"])

        self.ops_sem_data_com_semana["NSEM"] = self.ops_sem_data_com_semana["SEMANA_ENTREGA"].str.slice(
            0, 2).astype(int)
        self.ops_sem_data_com_semana["NANO"] = self.ops_sem_data_com_semana["SEMANA_ENTREGA"].str.slice(
            2, 6).astype(int)
        self.ops_sem_data_com_semana["FDOY"] = pd.to_datetime(
            dict(year=self.ops_sem_data_com_semana["NANO"], month=1, day=1))
        self.ops_sem_data_com_semana["FDOYWD"] = self.ops_sem_data_com_semana["FDOY"].dt.weekday
        self.ops_sem_data_com_semana["ENTREGA_NOVA"] = self.ops_sem_data_com_semana["FDOY"] + pd.to_timedelta(
            self.ops_sem_data_com_semana["NSEM"] * 7 - 3 - self.ops_sem_data_com_semana["FDOYWD"], 'D')
        self.ops_sem_data_com_semana = self.ops_sem_data_com_semana["ENTREGA"].fillna(
            self.ops_sem_data_com_semana["ENTREGA_NOVA"])

        self.ops_pendentes["ENTREGA"] = self.ops_pendentes["ENTREGA"].fillna(
            self.ops_sem_data_com_semana)

    def timeline(self, CPD_MP):
        def create_timeline(CPD_MP):
            def get_timeline_dates_series(CPD_MP):
                # Cria DataSeries com as todas as datas existentes
                # entre hoje e o limite do horizonte de programação
                def get_item_timeline_limit(CPD_MP):
                    # Define o horizonte de programação para o item em análise
                    item_timeline_limit = self.feedstock_to_analyze.loc[self.feedstock_to_analyze[
                        "CPD_MP"] == CPD_MP]["HORIZONTE_PROGRAMACAO"].iloc[0] * 7

                    return item_timeline_limit

                timeline_dates_series = pd.DataFrame(
                    {
                        "ENTREGA":
                        pd.date_range(
                            pd.datetime.today().strftime('%Y-%m-%d'),
                            periods=get_item_timeline_limit(CPD_MP)
                        )
                    }
                )

                return timeline_dates_series

            def get_pending_purchase_orders(CPD_MP):
                # Busca as OCs somente do CPD em analise e soma as quantidades pendentes das ocs agrupando por data.
                pending_purchase_orders = self.open_purchase_orders.loc[self.open_purchase_orders["CPD_MP"] == CPD_MP][[
                    "CPD_MP", "ENTREGA", "QTD_PENDENTE_OC"]].groupby(["CPD_MP", "ENTREGA"]).sum().reset_index()

                return pending_purchase_orders

            def get_pending_production_orders(CPD_MP):
                # Busca as OPs somente do CPD em analise e soma as quantidades pendentes das ops agrupando por data.
                pending_production_orders = self.ops_pendentes[self.ops_pendentes["CPD_MP"] == CPD_MP][[
                    "CPD_MP", "ENTREGA", "COMPROMETIDO"]].groupby(["CPD_MP", "ENTREGA"]).sum().reset_index()

                return pending_production_orders

            # Define um array com os DataFrames que serão mesclados
            dataframes_to_merge = [get_timeline_dates_series(
                CPD_MP), get_pending_purchase_orders(CPD_MP), get_pending_production_orders(CPD_MP)]

            # Mescla os DataFrames instanciando a timeline do item no objeto self.tl
            self.tl = reduce(lambda left, right: pd.merge(
                left, right, how="outer", sort="ENTREGA").fillna({"CPD_MP": CPD_MP}), dataframes_to_merge)

            def normalize_timeline_fields_NaN_to_zero():
                # Normaliza as quantidades pendentes para ZERO onde forem NaN
                self.tl = self.tl.fillna({"QTD_PENDENTE_OC": 0, "COMPROMETIDO": 0}).sort_values(
                    by="ENTREGA", ascending=True)

            normalize_timeline_fields_NaN_to_zero()

            def create_balance_fields():
                self.tl["SALDO_INICIAL"] = 0
                self.tl["SALDO_FINAL"] = 0

            create_balance_fields()

            def limit_timeline_dates_to_programming_horizon(CPD_MP):
                self.tl = self.tl.set_index("ENTREGA").loc[:get_timeline_dates_series(
                    CPD_MP).iloc[-1].values[0]].reset_index()

            limit_timeline_dates_to_programming_horizon(CPD_MP)

            return self.tl

        def calculate_first_balances_for_timeline(CPD_MP):
            # Define o saldo inicial da primeira data no self.tl
            self.tl.loc[0, "SALDO_INICIAL"] = self.feedstock_to_analyze.loc[self.feedstock_to_analyze["CPD_MP"]
                                                                            == CPD_MP, "SALDO_INICIAL"].to_numpy()

            # Define o saldo final da primeira data no self.tl
            self.tl.loc[0, "SALDO_FINAL"] = self.tl.loc[0, "SALDO_INICIAL"] - \
                self.tl.loc[0, "COMPROMETIDO"] + \
                self.tl.loc[0, "QTD_PENDENTE_OC"]

            return self.tl

        def calculate_balances_for_each_date_in_timeline():
            # Calcula os saldos final e inicial para as demais linhas no self.tl
            for l in range(1, len(self.tl)):
                self.tl.loc[l, "SALDO_INICIAL"] = self.tl.loc[l -
                                                              1, "SALDO_FINAL"]
                self.tl.loc[l, "SALDO_FINAL"] = self.tl.loc[l, "SALDO_INICIAL"] - \
                    self.tl.loc[l, "COMPROMETIDO"] + \
                    self.tl.loc[l, "QTD_PENDENTE_OC"]

        def flag_dates_with_missing():
            # Cria a coluna que indica SE e QUANDO ira faltar MP na self.tl
            self.tl["FALTA"] = self.tl["SALDO_FINAL"] <= 0

        def count_dates_with_lack():
            # Checa se haverá falta em alguma data na TL
            will_lack = len(self.tl[self.tl["FALTA"] == True])

            return will_lack

        create_timeline(CPD_MP)
        calculate_first_balances_for_timeline(CPD_MP)
        calculate_balances_for_each_date_in_timeline()
        flag_dates_with_missing()

        # Se houver falta na TL, verificar as datas e OPs em que havera e registrar no relatorio de faltas
        if count_dates_with_lack() > 0:
            def get_item_partnumber(CPD_MP):
                item_partnumber = self.feedstock_to_analyze.loc[
                    self.feedstock_to_analyze["CPD_MP"] == CPD_MP, "CODIGO_MP"].iloc[0]
                return item_partnumber

            def get_item_currency(CPD_MP):
                item_currency = self.feedstock_to_analyze.loc[
                    self.feedstock_to_analyze["CPD_MP"] == CPD_MP, "SIMBOLO"].iloc[0]

                return item_currency

            def get_item_unitary_cost(CPD_MP):
                item_unitary_cost = self.feedstock_to_analyze.loc[
                    self.feedstock_to_analyze["CPD_MP"] == CPD_MP, "CUSTO_MP"].iloc[0]

                return item_unitary_cost

            def get_lack_dates():
                # Define as datas em que haverá falta de MP
                lack_dates = self.tl[self.tl["FALTA"]][["ENTREGA", "CPD_MP"]]

                return lack_dates

            def get_first_lack_date():
                # Define a primeira data em que haverá falta de MP
                first_lack_date = self.lack_dates["ENTREGA"].min()

                return first_lack_date

            def get_first_lack_date_balance():
                first_lack_date_balance = float(
                    self.tl.loc[self.tl["ENTREGA"] == get_first_lack_date(), "SALDO_FINAL"].iloc[0])

                return first_lack_date_balance

            def check_if_item_needs_purchase_before_leadtime(CPD_MP, first_lack_date):
                def get_item_leadtime():
                    item_leadtime = int(
                        self.feedstock_to_analyze.loc[self.feedstock_to_analyze["CPD_MP"] == CPD_MP, "LEADTIME"].iloc[0]) * 7

                    return item_leadtime

                def get_item_leadtime_deadline_date():
                    item_leadtime_deadline_date = datetime.today(
                    ) + timedelta(days=self.report_data["leadtime"])
                    return item_leadtime_deadline_date

                self.report_data["leadtime"] = get_item_leadtime()

                if first_lack_date < get_item_leadtime_deadline_date():
                    self.report_data["item_needs_purchase_before_leadtime"] = True
                    return True
                else:
                    return False

            def get_productions_orders_with_lack(CPD_MP):
                # Filtra as OPs pendentes da Matéria Prima que têm suas datas de entrega após a primeira data em que haverá falta de MP
                production_orders_with_lack = pd.merge(self.lack_dates, self.ops_pendentes.loc[self.ops_pendentes["CPD_MP"] == CPD_MP].set_index(
                    "ENTREGA"), on=["ENTREGA", "CPD_MP"], how="inner")

                return production_orders_with_lack

            def get_total_missing_quantity(CPD_MP):
                total_missing_quantity = get_productions_orders_with_lack(CPD_MP).sum()[
                    "COMPROMETIDO"]
                return total_missing_quantity

            def get_future_purchase_orders(CPD_MP, first_lack_date):
                future_purchase_orders = self.open_purchase_orders[self.open_purchase_orders["CPD_MP"] == CPD_MP].set_index(
                    "ENTREGA", drop=1).sort_values(by="ENTREGA", axis=0, ascending=True)[first_lack_date:].reset_index()

                return future_purchase_orders

            def calculate_cumsum_of_future_purchase_orders():
                self.future_purchase_orders.loc[:,
                                                "ACUMULADO_OCS"] = self.future_purchase_orders["QTD_PENDENTE_OC"].cumsum()

            self.report_data = dict()

            self.report_data["CPD"] = CPD_MP
            self.report_data["item_partnumber"] = get_item_partnumber(CPD_MP)
            self.report_data["moeda"] = get_item_currency(CPD_MP)
            self.report_data["custo_unit"] = get_item_unitary_cost(CPD_MP)

            self.report_data["timeline"] = self.tl.reset_index().to_dict(
                orient="records")

            self.lack_dates = get_lack_dates()

            self.report_data["first_lack_date"] = get_first_lack_date()

            self.report_data["first_lack_date_balance"] = get_first_lack_date_balance(
            )

            check_if_item_needs_purchase_before_leadtime(
                CPD_MP=CPD_MP, first_lack_date=get_first_lack_date())

            self.report_data["quantidade_falta"] = get_total_missing_quantity(
                CPD_MP)

            self.future_purchase_orders = get_future_purchase_orders(
                CPD_MP, get_first_lack_date())

            if len(self.future_purchase_orders) > 0:
                self.report_data["ocs_futuras"] = self.future_purchase_orders.reset_index(
                ).to_dict(orient="records")

                def get_anticipable_amount():
                    calculate_cumsum_of_future_purchase_orders()

                    anticipable_amount = self.future_purchase_orders["ACUMULADO_OCS"].max(
                    )

                    return anticipable_amount

                def get_purchase_orders_to_anticipate():
                    purchase_orders_to_anticipate = self.future_purchase_orders.set_index(
                        "ENTREGA").loc[:self.future_purchase_orders[self.future_purchase_orders["ACUMULADO_OCS"] >= get_total_missing_quantity(CPD_MP)].iloc[0]["ENTREGA"]].reset_index()

                    return purchase_orders_to_anticipate

                if get_anticipable_amount() >= get_total_missing_quantity(CPD_MP):
                    self.report_data["acao_sugerida"] = "Antecipar"
                    self.anticipable_purchase_orders = get_purchase_orders_to_anticipate()

                    self.report_data["ocs_para_antecipar"] = self.anticipable_purchase_orders.to_dict(
                        orient="records")

                    self.report_data["quantidade_antecipar"] = self.anticipable_purchase_orders["QTD_PENDENTE_OC"].sum(
                    )
                    self.report_data["custo_acao_antecipar"] = self.report_data["quantidade_antecipar"] * \
                        get_item_unitary_cost(CPD_MP)
                elif 0 < get_anticipable_amount() < get_total_missing_quantity(CPD_MP):
                    self.report_data["acao_sugerida"] = "Antecipar/Comprar"
                    self.anticipable_purchase_orders = self.future_purchase_orders.reset_index()

                    self.report_data["ocs_para_antecipar"] = self.anticipable_purchase_orders.to_dict(
                        orient="records")

                    self.report_data["quantidade_antecipar"] = self.anticipable_purchase_orders["QTD_PENDENTE_OC"].sum(
                    )
                    self.report_data["custo_acao_antecipar"] = self.report_data["quantidade_antecipar"] * \
                        get_item_unitary_cost(CPD_MP)

                    remaining_missing_quantity = get_total_missing_quantity(
                        CPD_MP) - self.report_data["quantidade_antecipar"]

                    self.report_data["quantidade_comprar"] = self.get_purchase_quantity(
                        CPD_MP=CPD_MP, missing_quantity=remaining_missing_quantity)
                    self.report_data["custo_acao_comprar"] = self.report_data["quantidade_comprar"] * \
                        get_item_unitary_cost(CPD_MP)

            else:
                self.report_data["acao_sugerida"] = "Comprar"

                self.report_data["quantidade_comprar"] = self.get_purchase_quantity(
                    CPD_MP=CPD_MP, missing_quantity=get_total_missing_quantity(CPD_MP))
                self.report_data["custo_acao_comprar"] = self.report_data["quantidade_comprar"] * \
                    get_item_unitary_cost(CPD_MP)

            production_orders_with_lack = get_productions_orders_with_lack(
                CPD_MP)

            self.report_data["relatorio"] = production_orders_with_lack.reset_index(
            ).to_dict(orient="records")

            return self.report_data

        return dict()

    def max_stock_calculation(self, CPD_MP):
        def get_item_parameters(CPD_MP):
            parameters = dict()

            parameters["num_of_workdays"] = self.feedstock_to_analyze.loc[self.feedstock_to_analyze["CPD_MP"]
                                                                          == CPD_MP, "MESES_CONSUMO_MRP"].iloc[0]
            parameters["purchasing_frequency"] = self.feedstock_to_analyze.loc[self.feedstock_to_analyze["CPD_MP"]
                                                                               == CPD_MP, "PERIODICIDADE"].iloc[0]
            parameters["service_factor"] = self.feedstock_to_analyze.loc[self.feedstock_to_analyze["CPD_MP"]
                                                                         == CPD_MP, "FATOR_SERVICO"].iloc[0]
            parameters["security_stock_factor"] = self.feedstock_to_analyze.loc[self.feedstock_to_analyze["CPD_MP"]
                                                                                == CPD_MP, "FES"].iloc[0]

            return parameters

        def get_date_subtracting_workdays(from_date, num_of_workdays_to_subtract):
            current_date = from_date
            num_of_workdays_to_subtract = num_of_workdays_to_subtract

            while num_of_workdays_to_subtract > 0:
                current_date -= timedelta(days=1)

                if current_date.weekday() >= 5:
                    continue

                num_of_workdays_to_subtract -= 1

            return current_date

        def get_item_sales_amount_in_period(CPD_MP, from_date, to_date):
            query = """
                        SELECT
                            SUM(ITE.QUANTIDADE)
                        FROM
                            MOV_ITEM ITE
                            JOIN MOV_DOC DOC ON DOC.PK_DOC = ITE.FK_DOC
                        WHERE
                            ITE.FK_PRO = {} AND
                            DOC.DATAEXP >= '{}' AND
                            DOC.DATAEXP < '{}' AND
                            DOC.SOMDIMEST = 'D' AND
                            DOC.FK_TIP = 6
                        GROUP BY
                            ITE.FK_PRO
                        """.format(
                str(CPD_MP),
                str(from_date),
                str(to_date)
            )

            try:
                sales_amount = float(
                    self.db.connection.cursor().execute(query).fetchone()[0])
            except:
                sales_amount = 0

            return sales_amount

        def get_item_sales_average_in_period(CPD_MP, from_date, to_date, num_of_workdays):
            sales_amount = get_item_sales_amount_in_period(
                CPD_MP=CPD_MP,
                from_date=from_date,
                to_date=to_date
            )

            sales_average = float(sales_amount / num_of_workdays * 20)

            return sales_average

        def get_item_sales_standard_deviation_in_period(CPD_MP, from_date, to_date):
            query = """
                        SELECT
                            SUM(ITE.QUANTIDADE) QUANTIDADE
                        FROM
                            MOV_ITEM ITE
                            JOIN MOV_DOC DOC ON DOC.PK_DOC = ITE.FK_DOC
                        WHERE
                            ITE.FK_PRO = {} AND
                            DOC.DATAEXP >= '{}' AND
                            DOC.DATAEXP < '{}' AND
                            DOC.SOMDIMEST = 'D' AND
                            DOC.FK_TIP = 6
                        GROUP BY
                            DOC.DATAEXP
                        """.format(
                str(CPD_MP),
                str(from_date),
                str(to_date)
            )

            daily_sales = pd.read_sql(query, self.db.connection)

            sales_standard_deviation = daily_sales["QUANTIDADE"].std()
            return sales_standard_deviation

        yesterday = datetime.today().date() - timedelta(days=1)

        item_parameters = get_item_parameters(CPD_MP)

        start_date = get_date_subtracting_workdays(
            yesterday, item_parameters["num_of_workdays"])

        sales_amount = get_item_sales_amount_in_period(
            CPD_MP=CPD_MP,
            from_date=start_date,
            to_date=yesterday)

        sales_average = get_item_sales_average_in_period(
            CPD_MP=CPD_MP,
            from_date=start_date,
            to_date=yesterday,
            num_of_workdays=item_parameters["num_of_workdays"])

        sales_standard_deviation = get_item_sales_standard_deviation_in_period(
            CPD_MP=CPD_MP,
            from_date=start_date,
            to_date=yesterday)

        security_stock = sales_standard_deviation * \
            item_parameters["service_factor"]

        purchase_order_point = sales_average / 30 * \
            item_parameters["security_stock_factor"] + security_stock

        max_stock = purchase_order_point + \
            (sales_average * item_parameters["purchasing_frequency"])

        return max_stock

    def get_purchase_quantity(self, CPD_MP, missing_quantity):
        item_moq = self.feedstock_to_analyze.loc[self.feedstock_to_analyze["CPD_MP"]
                                                 == CPD_MP, "MOQ"].iloc[0]
        self.report_data["item_moq"] = item_moq

        def alert_if_purchase_quantity_exceeds_moq(missing_quantity, purchase_quantity, item_moq):
            self.report_data["purchase_quantity_exceeds_moq_alert"] = True
            self.report_data["how_much_purchasing_exceeds_missing_quantity"] = purchase_quantity - missing_quantity

            item_unitary_price = self.feedstock_to_analyze.loc[
                self.feedstock_to_analyze["CPD_MP"] == CPD_MP, "CUSTO_MP"].iloc[0]

            self.report_data["how_much_costs_the_purchasing_that_exceeds_missing_quantity"] = self.report_data[
                "how_much_purchasing_exceeds_missing_quantity"] * item_unitary_price
            return True

        def alert_if_purchase_quantity_exceeds_max_stock(purchase_quantity, max_stock):
            self.report_data["purchase_quantity_exceeds_max_stock_alert"] = True
            self.report_data["how_much_purchasing_exceeds_max_stock"] = purchase_quantity - max_stock

            item_unitary_price = self.feedstock_to_analyze.loc[
                self.feedstock_to_analyze["CPD_MP"] == CPD_MP, "CUSTO_MP"].iloc[0]

            self.report_data["how_much_costs_the_purchasing_that_exceeds_max_stock"] = self.report_data[
                "how_much_purchasing_exceeds_max_stock"] * item_unitary_price
            return True

        try:
            max_stock = self.max_stock_calculation(CPD_MP)
        except:
            max_stock = 999999999

        self.report_data["max_stock"] = max_stock

        purchase_quantity = math.ceil(missing_quantity / item_moq) * item_moq

        self.report_data["quantidade_comprar"] = purchase_quantity

        if 0 < purchase_quantity < item_moq:
            alert_if_purchase_quantity_exceeds_moq(
                missing_quantity, purchase_quantity, item_moq)

        self.report_data["first_missing_date_final_balance_after_purchase"] = self.report_data["first_lack_date_balance"] + purchase_quantity

        if self.report_data["first_missing_date_final_balance_after_purchase"] > max_stock:
            alert_if_purchase_quantity_exceeds_max_stock(
                purchase_quantity, max_stock)

        return purchase_quantity
