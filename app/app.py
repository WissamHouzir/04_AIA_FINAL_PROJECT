import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go

### Config
st.set_page_config(
    page_title="Application de detection des fakes news sur le climat",
    page_icon="💳",
    layout="wide"
)
config = {'width': 'stretch'}

### Engine
engine = create_engine('postgresql://airflow:airflow@postgres:5432/airflow')

### Data
@st.cache_data(ttl=60)
def load_transaction_data():
    data = pd.read_sql(sql="SELECT * FROM climate_news_data", con=engine)
    data['date'] = pd.to_datetime(data['created_at'], format='%Y-%m-%d %H:%M:%S').dt.date
    return data

data = load_transaction_data()

### Streamlit pages
def dashboard():
    st.title("Suivi du contrôle des articles")
    if data.empty:
        st.warning("Veuillez démarrer d'abord le pipeline Airflow pour charger les données.")
    
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Nombre d'articles", data.shape[0], border=True, height='stretch')
        with col2:
            st.metric("Classés Vrai", data[data['pred_label']=='true'].shape[0], border=True, height='stretch')
        with col3:
            st.metric("Classés Faux", data[data['pred_label']=='fake'].shape[0], border=True, height='stretch')
        with col4:
            st.metric("Classés Biaisé", data[data['pred_label']=='biased'].shape[0], border=True, height='stretch')
        with col5:
            try:
                st.metric("Pourcentage d'infox", f"{round(data[data['pred_label']=='fake'].shape[0]/data.shape[0]*100, 2)}%", border=True, height='stretch')
            except ZeroDivisionError:
                st.metric("Pourcentage d'infox", 0, border=True, height='stretch')
    
        transaction_data = data.groupby(['date']).agg(
            articles=('created_at', 'count'),
            articles_vrai=('is_true', 'sum'),
            articles_faux=('is_fake', 'sum'),
            articles_biaises=('is_biased', 'sum')
            ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(x=transaction_data['date'], y=transaction_data['articles_vrai'], name='Vrai', marker_color='green'))
        fig.add_trace(go.Bar(x=transaction_data['date'], y=transaction_data['articles_biaises'], name='Biaisé', marker_color='orange'))
        fig.add_trace(go.Bar(x=transaction_data['date'], y=transaction_data['articles_faux'],name='Faux', marker_color='red'))
        fig.update_layout(
            barmode='group',
            xaxis_title='Heure',
            yaxis_title='Nombre'
        )
        st.plotly_chart(fig, config=config)

def performance_metrics():
    try:
        with open("/app/data/data_drift_report.html", "r", encoding="utf-8") as f:
            html_content = f.read()   
        components.html(html=html_content, height=3000)

    except FileNotFoundError:
        st.error("Aucun rapport disponible. Veuillez génerer le rapport via Airflow avant de pouvoir le visualiser.")

### Navigation
pages = {
    "Application de fact checking": [
    st.Page(dashboard, title="Synthèse du fact checking", icon="📊"),
    st.Page(performance_metrics, title="Performance du modèle", icon="📉")
    ]
    }

pg = st.navigation(pages)

pg.run()