import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'db' / 'bluestock_mf.db'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'

engine = create_engine(f"sqlite:///{DB_PATH}")

def calculate_and_export():
    print("Running batch quantitative analysis engine...")
    df_nav = pd.read_sql("SELECT * FROM fact_nav", engine)
    df_bench = pd.read_sql("SELECT * FROM dim_benchmark WHERE index_name = 'NIFTY100'", engine)
    df_perf = pd.read_csv(BASE_DIR / 'data' / 'raw' / '07_scheme_performance.csv')
    
    pivot = df_nav.pivot(index='date', columns='amfi_code', values='nav').pct_change().dropna()
    bench_ret = df_bench.set_index('date')['close_value'].pct_change().dropna()
    
    results = []
    rf_daily = 0.065 / 252
    
    for code in pivot.columns:
        fund_ret = pivot[code]
        sharpe = ((fund_ret.mean() - rf_daily) / fund_ret.std()) * np.sqrt(252)
        
        downside = fund_ret[fund_ret < 0]
        sortino = ((fund_ret.mean() * 252 - 0.065) / (downside.std() * np.sqrt(252)))
        max_dd = ( (1 + fund_ret).cumprod() / (1 + fund_ret).cumprod().cummax() - 1 ).min()
        
        # Align data strings for exact regression matching
        data = pd.DataFrame({'fund': fund_ret, 'bench': bench_ret}).dropna()
        slope, intercept, _, _, _ = stats.linregress(data['bench'], data['fund'])
        
        results.append({
            'amfi_code': code, 
            'Sharpe_Ratio': sharpe, 
            'Sortino': sortino, 
            'MaxDD': max_dd, 
            'Alpha': intercept * 252, 
            'Beta': slope
        })
        
    df_res = pd.DataFrame(results).merge(df_perf, on='amfi_code')
    
    # Calculate scorecard composite ranks
    for col in ['return_3yr_pct', 'Sharpe_Ratio', 'Alpha', 'expense_ratio_pct', 'MaxDD']:
        asc = True if col in ['expense_ratio_pct', 'MaxDD'] else False
        df_res[f'{col}_rank'] = df_res[col].rank(pct=True, ascending=asc) * 100

    df_res['Final_Score'] = (
        0.30 * df_res['return_3yr_pct_rank'] + 
        0.25 * df_res['Sharpe_Ratio_rank'] + 
        0.20 * df_res['Alpha_rank'] + 
        0.15 * df_res['expense_ratio_pct_rank'] + 
        0.10 * df_res['MaxDD_rank']
    )
    
    # Export assets
    df_res[['amfi_code', 'Alpha', 'Beta']].to_csv(PROCESSED_DIR / 'alpha_beta.csv', index=False)
    df_res[['amfi_code', 'scheme_name', 'Final_Score']].to_csv(PROCESSED_DIR / 'fund_scorecard.csv', index=False)
    print("✅ Automated data processing metrics successfully updated.")

if __name__ == "__main__":
    calculate_and_export()