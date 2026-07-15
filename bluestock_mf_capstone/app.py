import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Bluestock MF Analytics", page_icon="📈", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Loads and merges the star schema data."""
    data_dir = Path('data/processed')
    
    # Load Fact and Dimension tables
    fact_df = pd.read_csv(data_dir / 'fact_nav_clean.csv')
    dim_df = pd.read_csv(data_dir / 'dim_fund_clean.csv')
    
    # Dynamically locate columns
    date_col = [col for col in fact_df.columns if 'date' in col.lower()][0]
    id_col = [col for col in fact_df.columns if 'code' in col.lower() or 'id' in col.lower()][0]
    nav_col = [col for col in fact_df.columns if 'nav' in col.lower()][0]
    name_col = [col for col in dim_df.columns if 'name' in col.lower()][0]
    
    # Merge to ensure we have readable category names instead of integer codes
    df = pd.merge(fact_df, dim_df, on=id_col, how='inner')
    df[date_col] = pd.to_datetime(df[date_col])
    df[nav_col] = pd.to_numeric(df[nav_col], errors='coerce')
    
    return df, date_col, nav_col, name_col, id_col

# Load data
try:
    df, date_col, nav_col, name_col, id_col = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"⚠️ Error loading data: {e}. Please check your data/processed folder.")
    data_loaded = False

# --- DASHBOARD UI ---
st.title("📈 Bluestock Mutual Fund Analytics")
st.markdown("An interactive business intelligence dashboard for institutional risk analysis.")

if data_loaded:
    # Create Tabs matching your Final Report structure
    tab1, tab2 = st.tabs(["Executive Overview", "Deep-Dive Analytics"])
    
    # --- TAB 1: EXECUTIVE OVERVIEW ---
    with tab1:
        st.header("Industry Macro Trends")
        
        # High-level KPIs
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Funds Tracked", value=df[id_col].nunique())
        with col2:
            st.metric(label="Total NAV Records", value=f"{len(df):,}")
        with col3:
            min_date, max_date = df[date_col].min(), df[date_col].max()
            st.metric(label="Data Range", value=f"{min_date.year} - {max_date.year}")
            
        st.divider()
        
        # Sector/Category Distribution
        st.subheader("Fund Category Distribution")
        category_col = [col for col in df.columns if 'category' in col.lower()][0]
        cat_counts = df[category_col].value_counts()
        st.bar_chart(cat_counts, color="#20C997")

    # --- TAB 2: DEEP-DIVE ANALYTICS ---
    with tab2:
        st.header("Fund Risk & Performance Drill-Through")
        
        # Filter UI: Select box uses the string names, not integers
        fund_list = sorted(df[name_col].unique())
        selected_fund = st.selectbox("Select a Mutual Fund to Analyze:", options=fund_list)
        
        # Filter data based on selection
        fund_data = df[df[name_col] == selected_fund].sort_values(date_col).copy()
        
        # Calculate returns
        fund_data['daily_return'] = fund_data[nav_col].pct_change()
        
        # Display KPIs for the specific fund
        st.subheader(f"Metrics for {selected_fund}")
        c1, c2, c3 = st.columns(3)
        
        current_nav = fund_data[nav_col].iloc[-1]
        historical_var = fund_data['daily_return'].quantile(0.05) * 100
        volatility = fund_data['daily_return'].std() * np.sqrt(252) * 100
        
        c1.metric(label="Latest NAV", value=f"₹{current_nav:,.2f}")
        c2.metric(label="95% Daily VaR", value=f"{historical_var:.2f}%")
        c3.metric(label="Annualized Volatility", value=f"{volatility:.2f}%")
        
        # Plot NAV Trajectory
        st.markdown("### Historical NAV Trajectory")
        chart_data = fund_data.set_index(date_col)[[nav_col]]
        st.line_chart(chart_data, color="#0A2540")