"""
KCET CUTOFF DATASET - PYTHON USAGE GUIDE
=========================================

This script shows how to use the KCET comprehensive dataset
for analysis, filtering, and predictions.

Install: pip install pandas numpy matplotlib seaborn
"""

import pandas as pd
import numpy as np

# ============================================================
# 1. LOAD THE DATASET
# ============================================================
print("Loading KCET dataset...")
df = pd.read_csv("KCET_Complete_2010_2024_AllData.csv")

print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nFirst few rows:")
print(df.head())

# ============================================================
# 2. BASIC FILTERING
# ============================================================

# Get only 2024 data
df_2024 = df[df['Year'] == 2024]
print(f"\n2024 records: {len(df_2024):,}")

# Get only Round 1
df_r1 = df[df['Round'] == 'R1']
print(f"Round 1 records: {len(df_r1):,}")

# Get only General Merit category
df_gm = df[df['Category'] == 'GM']
print(f"GM category records: {len(df_gm):,}")

# Get specific college (UVCE)
df_uvce = df[df['College_Code'] == 'E001']
print(f"UVCE records: {len(df_uvce):,}")

# ============================================================
# 3. COMBINED FILTERING
# ============================================================

# Find UVCE CSE 2024 R1 GM
query = (df['Year'] == 2024) & \
        (df['College_Code'] == 'E001') & \
        (df['Round'] == 'R1') & \
        (df['Category'] == 'GM') & \
        (df['Course'].str.contains('COMPUTER SCIENCE', na=False))

result = df[query]
print(f"\nUVCE CSE 2024 R1 GM:")
print(result[['College_Name', 'Course', 'Cutoff_Rank', 'Data_Source']])

# ============================================================
# 4. FIND TOP COLLEGES
# ============================================================

# Top 10 colleges by most competitive CSE cutoff (2024, R1, GM)
top_cse = df[(df['Year'] == 2024) & 
             (df['Round'] == 'R1') & 
             (df['Category'] == 'GM') &
             (df['Course'].str.contains('COMPUTER SCIENCE', na=False))]

top_10 = top_cse.nsmallest(10, 'Cutoff_Rank')[['College_Name', 'Cutoff_Rank', 'Location']]
print("\nTop 10 CSE Colleges (2024, R1, GM):")
print(top_10.to_string(index=False))

# ============================================================
# 5. CATEGORY COMPARISON
# ============================================================

# Compare cutoffs for same college, course, year across categories
comparison = df[(df['College_Code'] == 'E001') & 
                (df['Year'] == 2024) & 
                (df['Round'] == 'R1') &
                (df['Course'].str.contains('COMPUTER SCIENCE', na=False))]

print("\nUVCE CSE - Cutoffs by Category (2024, R1):")
for cat in ['GM', '1G', '2AG', '3AG', 'SCG', 'STG']:
    rank = comparison[comparison['Category'] == cat]['Cutoff_Rank'].values
    if len(rank) > 0:
        print(f"  {cat:3s}: Rank {rank[0]:6d}")

# ============================================================
# 6. ROUND COMPARISON
# ============================================================

# See how cutoffs change across rounds
rounds_comp = df[(df['College_Code'] == 'E001') & 
                 (df['Year'] == 2024) & 
                 (df['Category'] == 'GM') &
                 (df['Course'].str.contains('COMPUTER SCIENCE', na=False))]

print("\nUVCE CSE - Cutoffs by Round (2024, GM):")
for rnd in ['R1', 'R2', 'R3']:
    rank = rounds_comp[rounds_comp['Round'] == rnd]['Cutoff_Rank'].values
    if len(rank) > 0:
        print(f"  {rnd}: Rank {rank[0]:6d}")

# ============================================================
# 7. TREND ANALYSIS - 15 YEAR HISTORY
# ============================================================

print("\nUVCE CSE - 15 Year Trend (R1, GM):")
trend = df[(df['College_Code'] == 'E001') &
           (df['Round'] == 'R1') &
           (df['Category'] == 'GM') &
           (df['Course'].str.contains('COMPUTER SCIENCE', na=False))]

trend = trend.sort_values('Year')[['Year', 'Cutoff_Rank', 'Data_Source']]
for _, row in trend.iterrows():
    print(f"  {int(row['Year'])}: {int(row['Cutoff_Rank']):6d} ({row['Data_Source']})")

# ============================================================
# 8. STATISTICS & AGGREGATION
# ============================================================

# Average cutoff by college (2024, R1, GM)
avg_by_college = df[(df['Year'] == 2024) & 
                    (df['Round'] == 'R1') & 
                    (df['Category'] == 'GM')].groupby('College_Name')['Cutoff_Rank'].mean()

print("\nAverage GM Cutoff by College (2024, R1):")
print(f"  Most competitive: {avg_by_college.idxmin()} - {avg_by_college.min():.0f}")
print(f"  Least competitive: {avg_by_college.idxmax()} - {avg_by_college.max():.0f}")

# ============================================================
# 9. ELIGIBILITY CHECK
# ============================================================

def check_eligibility(rank, year=2024, round_name='R3', category='GM'):
    """
    Check which colleges a candidate with given rank is eligible for
    (assuming they want CSE, Round 3, and specific category)
    """
    eligible = df[(df['Year'] == year) & 
                  (df['Round'] == round_name) & 
                  (df['Category'] == category) &
                  (df['Cutoff_Rank'] >= rank) &
                  (df['Course'].str.contains('COMPUTER SCIENCE', na=False))]
    
    return eligible[['College_Name', 'Cutoff_Rank', 'Location']].drop_duplicates('College_Name').head(20)

print("\nColleges eligible for Rank 5000 (CSE, 2024, R3, GM):")
eligible_colleges = check_eligibility(5000, year=2024, round_name='R3', category='GM')
print(eligible_colleges.to_string(index=False))

# ============================================================
# 10. EXPORT & SAVE
# ============================================================

# Filter and export to new CSV
custom_data = df[(df['Year'] == 2024) & (df['Category'] == 'GM')]
custom_data.to_csv("kcet_2024_gm_only.csv", index=False)
print("\nExported: kcet_2024_gm_only.csv")

print("\n✅ Analysis complete!")
