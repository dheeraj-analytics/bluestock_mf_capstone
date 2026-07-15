# Bluestock Mutual Fund Analytics: End-to-End Data Pipeline

## 📊 Project Overview
The **Bluestock Mutual Fund Analytics** project is an end-to-end data engineering and quantitative analysis pipeline. It automates the extraction of historical Net Asset Value (NAV) data for 40 top-performing Indian mutual funds, transforms the data for missing-value continuity (handling weekends/holidays), and loads it into a centralized SQLite data warehouse. 

The project culminates in a composite performance scorecard (ranking funds by Sharpe Ratio, Jensen's Alpha, and Maximum Drawdown) and an interactive Business Intelligence dashboard.

## 🗂️ Folder Structure
```text
bluestock_mf_capstone/
├── data/
│   ├── raw/                 # Original downloaded API JSON/CSVs
│   ├── processed/           # Cleaned and forward-filled CSVs
│   └── db/                  # SQLite database location (ignored in git)
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
├── scripts/
│   ├── etl_pipeline.py      # Automated extraction and transformation script
│   ├── compute_metrics.py   # Calculates Sharpe, Alpha, and 95% VaR
│   └── recommender.py       # Recommends funds based on risk profiles
├── sql/
│   └── schema.sql           # Database table creation scripts
├── dashboard/
│   └── app.py               # Streamlit interactive dashboard
├── reports/
│   ├── Final_Report_Extended.pdf
│   └── Presentation.pptx
└── README.md
