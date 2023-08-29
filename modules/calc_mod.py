# Default imports

# External imports
from yahooquery import Ticker
import streamlit as st


@st.cache_data(ttl=3600, show_spinner="Fetching data from API...")
def y_stock(stock_name):
    # Getting data
    try:
        stock_name = stock_name.lower().replace(' ', '')
        # Yahoo mostra total de açoes erradamente, mostra apenas o total de cada ticker. Abaixo somando de todos os
        # tickers para saber o total
        if stock_name.endswith(("3", "4", "5", "6", "11")):            # se for BR
            out_shares_ticker_list = [stock_name[0:4] + "3.sa", stock_name[0:4] + "4.sa", stock_name[0:4] + "5.sa",
                                      stock_name[0:4] + "6.sa"]
            stock_name = stock_name + ".sa"
            ticker = Ticker(stock_name)
            out_shares = Ticker(out_shares_ticker_list)
            estatisticas_shares = out_shares.key_stats
            total_shares = 0
            for shares in estatisticas_shares.keys():
                try:
                    total_shares += estatisticas_shares[shares].get(
                        "sharesOutstanding")
                except:
                    pass
            if total_shares == 0:
                total_shares = None
        else:  # se for Internacional
            ticker = Ticker(stock_name)
            total_shares = ticker.key_stats[stock_name].get(
                "sharesOutstanding")
        summary_details = ticker.summary_detail
        prices = ticker.price
        financeiro = ticker.financial_data
        estatisticas = ticker.key_stats

        # Sorting data

        nome_empresa = prices[stock_name].get('shortName')
        preco_atual = prices[stock_name].get(
            'regularMarketPrice') or float("NaN")
        dividendo_12m = summary_details[stock_name].get(
            'trailingAnnualDividendYield') or float("NaN")
        current_ratio = financeiro[stock_name].get(
            'currentRatio') or float("NaN")
        current_ratio = round(current_ratio, 2)
        debt_to_equity = financeiro[stock_name].get(
            'debtToEquity') or float("NaN")
        debt_to_equity = round(debt_to_equity / 100, 2)
        ROE = financeiro[stock_name].get("returnOnEquity") or float("NaN")
        ROE = round(ROE * 100, 2)
        VPA = estatisticas[stock_name].get('bookValue') or float("NaN")
        VPA = round(VPA, 2)
        net_income = estatisticas[stock_name].get(
            "netIncomeToCommon") or float("NaN")

        # Pegando crescimento dos lucros
        income_stat = ticker.income_statement()

        # TODO: Consertar o calculo do lucro (nao esta considerando os valores certos pois a lista tem tamanhos variados)
        df = income_stat[["asOfDate", "NetIncome"]].copy()
        df.set_index('asOfDate', inplace=True)
        crescimento_lucro_12m = ((df["NetIncome"][3] / df["NetIncome"][2]) - 1) if (df["NetIncome"][2] != 0) else 0
        crescimento_lucro_36m = ((
            df["NetIncome"][3] / df["NetIncome"][0]) ** (1 / 3) - 1)  if (df["NetIncome"][0] != 0) else 0

        ########### Gráficos ##############
        # Gráfico Lucro Líquido
        df_graph_lucro_liq = income_stat[["asOfDate", "NetIncome"]].copy()
        # Transformando em milhões para melhor caber no gráfico
        df_graph_lucro_liq["NetIncome"] = df_graph_lucro_liq["NetIncome"] / 1000000
        ll_1 = {"NetIncome": df_graph_lucro_liq.get("NetIncome").to_list()}
        ll_2 = {"asOfDate": df_graph_lucro_liq.get("asOfDate").to_list()}
        ll_2.update(ll_1)
        graph_lucro_liq = ll_2


        # Gráfico Patrimonio Liquido
        balance = ticker.balance_sheet()
        df_graph_patr_liq = balance[["asOfDate", "StockholdersEquity"]].copy()
        # Transformando em milhões para melhor caber no gráfico
        df_graph_patr_liq["StockholdersEquity"] = df_graph_patr_liq["StockholdersEquity"] / 1000000
        pl_1 = {"StockholdersEquity": df_graph_patr_liq.get(
            "StockholdersEquity").to_list()}
        patri_liq_12m = (pl_1.get('StockholdersEquity')
                         [-1] * 1000000) or float("NaN")
        patri_liq_12m_str = round(patri_liq_12m)
        pl_2 = {"asOfDate": df_graph_patr_liq.get("asOfDate").to_list()}
        pl_2.update(pl_1)
        graph_patr_liq = pl_2

        # Retrieve each company's profile information
        profile = ticker.asset_profile

        setor = profile[stock_name].get("sector")
        cidade = profile[stock_name].get("city")
        pais = profile[stock_name].get("country")
        website = profile[stock_name].get("website")
        resumo = profile[stock_name].get("longBusinessSummary")
        industria = profile[stock_name].get("industry")

        # share_relation para conseguir corrigir os dados: LPA etc
        real_eps = round(net_income / total_shares, 2)
        real_PL = round(preco_atual / real_eps, 2)

        # Calculations
        peg_12m = round(real_PL / (crescimento_lucro_12m * 100), 2)  if (crescimento_lucro_12m != 0) else 0
        peg_36m = round(real_PL / (crescimento_lucro_36m * 100), 2)  if (crescimento_lucro_36m != 0) else 0
        preco_vp = round(preco_atual / VPA, 2)
        pl_p_vp = round(real_PL * preco_vp, 2)
        dividend = round(dividendo_12m * 100, 2)
        total_shares_str = total_shares
        net_income_str = net_income

        data_dict = {"nome_empresa": nome_empresa, "preco_atual": preco_atual, "real_PL": real_PL,
                     "preco_vp": preco_vp, "pl_p_vp": pl_p_vp, "dividend": dividend, "real_eps": real_eps,
                     "VPA": VPA, "ROE": ROE, "current_ratio": current_ratio, "debt_to_equity": debt_to_equity,
                     "net_income_str": net_income_str, "patri_liq_12m_str": patri_liq_12m_str, "total_shares_str": total_shares_str, "peg_12m": peg_12m,
                     "peg_36m": peg_36m, "graph_lucro_liq": graph_lucro_liq, "graph_patr_liq": graph_patr_liq,
                     "setor": setor, "cidade": cidade, "pais": pais, "website": website, "resumo": resumo, "industria": industria}

        return data_dict

    except Exception as e:
        st.toast(f"Error: , {e}, {e.__class__}", icon="❗")
        return None