import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="Bluestock MF Analytics", page_icon="🏦", layout="wide")

# Custom CSS to make the dashboard look like a pro financial terminal
st.markdown("""
    <style>
    .stMetric {
        background-color: #f4f6f9;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #20C997;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { color: #0A2540; font-family: 'Arial', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Loads and merges the star schema data, ensuring categorical names are displayed."""
    data_dir = Path('data/processed')
    
    fact_df = pd.read_csv(data_dir / 'fact_nav_clean.csv')
    dim_df = pd.read_csv(data_dir / 'dim_fund_clean.csv')
    
    date_col = [col for col in fact_df.columns if 'date' in col.lower()][0]
    id_col = [col for col in fact_df.columns if 'code' in col.lower() or 'id' in col.lower()][0]
    nav_col = [col for col in fact_df.columns if 'nav' in col.lower()][0]
    name_col = [col for col in dim_df.columns if 'name' in col.lower()][0]
    category_col = [col for col in dim_df.columns if 'category' in col.lower()][0]
    
    # Merge to ensure we have readable category and fund names instead of integer codes
    df = pd.merge(fact_df, dim_df, on=id_col, how='inner')
    df[date_col] = pd.to_datetime(df[date_col])
    df[nav_col] = pd.to_numeric(df[nav_col], errors='coerce')
    
    return df, date_col, nav_col, name_col, category_col

# Load data safely
try:
    df, date_col, nav_col, name_col, category_col = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"⚠️ Error loading data. Ensure fact_nav_clean.csv and dim_fund_clean.csv are in data/processed/. Error: {e}")
    data_loaded = False

# --- DASHBOARD UI ---
st.title("🏦 Bluestock Institutional Analytics Terminal")
st.markdown("Advanced quantitative analysis, downside risk modeling, and historical performance tracking for Indian Mutual Funds.")

if data_loaded:
    tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "🔎 Fund Deep-Dive", "⚠️ Risk & Drawdown Analysis"])
    
    # ==========================================
    # TAB 1: EXECUTIVE SUMMARY
    # ==========================================
    with tab1:
        st.header("Macro Industry Overview")
        
        # High-level KPIs in a 4-column grid
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Funds Analyzed", df[name_col].nunique())
        col2.metric("Total Data Points", f"{len(df):,}")
        col3.metric("Trading Days Tracked", df[date_col].nunique())
        col4.metric("Latest Date", df[date_col].max().strftime("%Y-%m-%d"))
            
        st.markdown("---")
        
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("Fund Category Distribution")
            cat_counts = df[category_col].value_counts().reset_index()
            cat_counts.columns = ['Category', 'Count']
            st.bar_chart(cat_counts.set_index('Category'), color="#20C997")
            
        with col_chart2:
            st.subheader("Platform Activity (Records over Time)")
            # Resample by month to show data density/growth
            monthly_records = df.set_index(date_col).resample('ME').size()
            st.area_chart(monthly_records, color="#0A2540")

    # ==========================================
    # TAB 2: FUND DEEP-DIVE
    # ==========================================
    with tab2:
        st.header("Individual Fund Performance Drill-Through")
        
        # Filter UI uses string names, completely hiding the internal ID codes
        fund_list = sorted(df[name_col].unique())
        selected_fund = st.selectbox("Search & Select a Mutual Fund:", options=fund_list)
        
        fund_data = df[df[name_col] == selected_fund].sort_values(date_col).copy()
        fund_data['daily_return'] = fund_data[nav_col].pct_change()
        
        # Calculate Advanced Metrics
        start_nav = fund_data[nav_col].iloc[0]
        end_nav = fund_data[nav_col].iloc[-1]
        days = (fund_data[date_col].iloc[-1] - fund_data[date_col].iloc[0]).days
        cagr = ((end_nav / start_nav) ** (365.25 / days) - 1) * 100 if days > 0 else 0
        
        historical_var = fund_data['daily_return'].quantile(0.05) * 100
        volatility = fund_data['daily_return'].std() * np.sqrt(252) * 100
        
        # 3-Column Metric Display
        c1, c2, c3 = st.columns(3)
        c1.metric(label="Latest NAV (₹)", value=f"₹{end_nav:,.2f}", delta=f"{fund_data['daily_return'].iloc[-1]*100:.2f}% Daily")
        c2.metric(label="Calculated CAGR", value=f"{cagr:.2f}%", delta="Annualized Growth")
        c3.metric(label="Annualized Volatility", value=f"{volatility:.2f}%", delta="Risk Indicator", delta_color="inverse")
        
        st.markdown("### Historical NAV Trajectory")
        st.line_chart(fund_data.set_index(date_col)[[nav_col]], color="#20C997", use_container_width=True)

    # ==========================================
    # TAB 3: RISK & DRAWDOWN ANALYSIS
    # ==========================================
    with tab3:
        st.header("Quantitative Downside Metrics")
        st.markdown(f"**Currently Analyzing:** `{selected_fund}`")
        
        # Calculate Drawdown
        fund_data['Peak'] = fund_data[nav_col].cummax()
        fund_data['Drawdown'] = (fund_data[nav_col] - fund_data['Peak']) / fund_data['Peak'] * 100
        max_drawdown = fund_data['Drawdown'].min()
        
        c1, c2 = st.columns(2)
        c1.metric(label="Maximum Drawdown", value=f"{max_drawdown:.2f}%", delta="Worst Peak-to-Trough Drop", delta_color="inverse")
        c2.metric(label="95% Value at Risk (VaR)", value=f"{historical_var:.2f}%", delta="Worst Expected Daily Loss", delta_color="inverse")
        
        col_risk1, col_risk2 = st.columns(2)
        
        with col_risk1:
            st.markdown("### Underwater Chart (Historical Drawdowns)")
            st.area_chart(fund_data.set_index(date_col)[['Drawdown']], color="#FF4B4B")
            
        with col_risk2:
            st.markdown("### Daily Returns Distribution (VaR Boundary)")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.histplot(fund_data['daily_return'].dropna() * 100, bins=50, color="#0A2540", kde=True, ax=ax)
            ax.axvline(historical_var, color='#FF4B4B', linestyle='--', linewidth=2, label=f'95% VaR ({historical_var:.2f}%)')
            ax.set_xlabel("Daily Return (%)")
            ax.set_ylabel("Frequency")
            ax.legend()
            st.pyplot(fig)