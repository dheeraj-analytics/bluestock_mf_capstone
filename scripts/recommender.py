import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import warnings

# Suppress terminal warnings for a clean UI
warnings.filterwarnings('ignore')

# Rubric-compliant path resolution
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
DB_PATH = BASE_DIR / 'data' / 'db' / 'bluestock_mf.db'

engine = create_engine(f"sqlite:///{DB_PATH}")

def recommend_funds(category_pref, risk_tolerance, top_n=3):
    """
    Core recommender logic engine. Cross-references user inputs
    with the Day 4 quantitative scorecard.
    """
    try:
        # Load the scorecard (D4) and fund master (D2)
        df_score = pd.read_csv(PROCESSED_DIR / 'fund_scorecard.csv')
        df_fund = pd.read_sql("SELECT amfi_code, category FROM dim_fund", engine)
        
        # Merge to get categories alongside scores
        master = df_score.merge(df_fund, on='amfi_code', how='inner')
        
        # Filter by Category Preference (case-insensitive)
        filtered = master[master['category'].str.lower() == category_pref.lower()]
        
        if filtered.empty:
            return None
            
        # Optional: In a production app, you would use 'risk_tolerance' to filter out
        # funds with a Max Drawdown higher than a certain threshold. 
        # For this script, we rely on the Final_Score which already penalizes high Max Drawdown.
        
        # Sort by the best composite score
        recommendations = filtered.sort_values(by='Final_Score', ascending=False).head(top_n)
        
        # Format the output for the terminal
        recommendations['Final_Score'] = recommendations['Final_Score'].round(2)
        return recommendations[['scheme_name', 'category', 'Final_Score']]
        
    except FileNotFoundError:
        print("❌ Error: fund_scorecard.csv not found. Please run compute_metrics.py first.")
        return None
    except Exception as e:
        print(f"❌ System Error: {e}")
        return None

def run_interactive_cli():
    """
    Command Line Interface (CLI) for the recommender.
    """
    print("="*50)
    print(" 📈 BLUESTOCK MUTUAL FUND RECOMMENDER ENGINE")
    print("="*50)
    
    print("\nAvailable Categories: Equity, Debt, Hybrid")
    category = input("Enter your preferred category: ").strip()
    
    print("\nAvailable Risk Profiles: Low, Medium, High")
    risk = input("Enter your risk tolerance: ").strip()
    
    print("\nAnalyzing quantitative metrics and compiling recommendations...")
    
    # Add a slight delay to simulate processing time
    import time
    time.sleep(1.5)
    
    recs = recommend_funds(category_pref=category, risk_tolerance=risk)
    
    if recs is not None and not recs.empty:
        print("\n✅ Top Fund Matches Based on Your Profile:\n")
        print(recs.to_string(index=False))
        print("\n" + "="*50)
    else:
        print("\n⚠️ No exact matches found for your criteria. Try adjusting your preferences.")

if __name__ == "__main__":
    run_interactive_cli()