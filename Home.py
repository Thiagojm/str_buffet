import streamlit as st
from PIL import Image
import pandas as pd
from modules.calc_mod import y_stock
import matplotlib.pyplot as plt

data = None

with st.container():
    col1, col2 = st.columns(2)
    col1.markdown('##')
    col1.markdown('##')
    col1.markdown('##')
    ticker = col1.text_input("Stock Ticker")
    btn1 = col1.button("Calculate")
    buff_mg = Image.open("src/img/buffet.png")
    col2.image(buff_mg)
    if btn1:
        data = y_stock(ticker)
        st.session_state["data"] = data
st.divider()

with st.container():
    if data:
        data_1 = {
            'nome_empresa': data['nome_empresa'],
            'preco_atual': data['preco_atual'],
            'real_PL': data['real_PL'],
            'preco_vp': data['preco_vp'],
            'pl_p_vp': data['pl_p_vp'],
            'dividend': data['dividend'],
            'real_eps': data['real_eps'],
            'VPA': data['VPA']
        }
        data_2 = {
            'ROE': data['ROE'],
            'current_ratio': data['current_ratio'],
            'debt_to_equity': data['debt_to_equity'],
            'net_income_str': data['net_income_str'],
            'patri_liq_12m_str': data['patri_liq_12m_str'],
            'total_shares_str': data['total_shares_str'],
            'peg_12m': data['peg_12m'],
            'peg_36m': data['peg_36m']
        }

        col3, col4 = st.columns(2)
        # Convert dictionary to table format and ensure string values for Arrow compatibility
        def safe_str(value):
            if pd.isna(value) or value is None:
                return "N/A"
            return str(value)

        table_data_1 = {"Data": list(data_1.keys()), "": [safe_str(v) for v in data_1.values()]}
        table_data_2 = {"Data": list(data_2.keys()), "": [safe_str(v) for v in data_2.values()]}

        # Fixed deprecation warning - replaced use_container_width with width
        col3.dataframe(table_data_1, hide_index=True, width='stretch')
        col4.dataframe(table_data_2, hide_index=True, width='stretch')

st.divider()

with st.container():
    if data:
        # Grafico lucro liquido
        graph_lucro_liq = pd.DataFrame(data["graph_lucro_liq"])
        graph_lucro_liq.dropna(subset=['NetIncome'], inplace=True)
        # Ensure proper data types for Arrow serialization
        graph_lucro_liq["asOfDate"] = pd.to_datetime(graph_lucro_liq["asOfDate"])
        graph_lucro_liq["NetIncome"] = graph_lucro_liq["NetIncome"].astype(float)
        st.dataframe(graph_lucro_liq)
        # Create the bar plot using matplotlib
        plt.figure()
        plt.bar(graph_lucro_liq['asOfDate'], graph_lucro_liq['NetIncome'],
                color='green', width=pd.Timedelta(days=70))
        plt.ylabel('Net Income')
        plt.title('Net Income Over Time')
        plt.xticks(graph_lucro_liq['asOfDate'], rotation=45)
        plt.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(plt)

        st.divider()

        # Grafico patrimonio liquido
        graph_patr_liq = pd.DataFrame(data["graph_patr_liq"])
        graph_patr_liq.dropna(subset=['StockholdersEquity'], inplace=True)
        # Ensure proper data types for Arrow serialization
        graph_patr_liq["asOfDate"] = pd.to_datetime(graph_patr_liq["asOfDate"])
        graph_patr_liq["StockholdersEquity"] = graph_patr_liq["StockholdersEquity"].astype(float)
        st.dataframe(graph_patr_liq)
        # Create the bar plot using matplotlib
        plt.figure()
        plt.bar(graph_patr_liq['asOfDate'],
                graph_patr_liq['StockholdersEquity'], width=pd.Timedelta(days=70))
        plt.ylabel('Equity')
        plt.title('Equity Over Time')
        plt.xticks(graph_patr_liq['asOfDate'], rotation=45)
        plt.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(plt)
