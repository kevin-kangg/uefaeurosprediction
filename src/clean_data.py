"""
Clean the data, transform the data and store the files in the data/processed folder

Author: Kevin Kang
"""
import os
import shutil
import pandas as pd
import numpy as np

def load_data():
    try:
        rankings_df = pd.read_csv("../data/raw/all_rankings_data.csv")
        results_df = pd.read_csv('../data/raw/results.csv')
        team_names_df = pd.read_csv('../data/raw/team_names.csv')

        # Perform data cleaning
        rankings_df["Nation"] = rankings_df["Nation"].str.replace("Türkiye", "Turkey") \
            .str.replace("N. Ireland", "Northern Ireland").str.replace("Czechia", "Czech Republic") \
            .str.replace("Bosnia", "Bosnia and Herzegovina").str.replace("USA", "United States") \
            .str.replace("Trinidad", "Trinidad and Tobago").str.replace("St. Kitts/Nevis", "Saint Kitts and Nevis") \
            .str.replace("St. Vincent", "Saint Vincent and the Grenadines").str.replace("Ireland", "Republic of Ireland") \
            .str.replace("China", "China PR").str.replace("Brazil", "Brazil").str.replace("Northern Republic of Ireland", "Northern Ireland") \
            .str.replace("U. A. E.", "United Arab Emirates")

        # Additional data cleaning steps for rankings DataFrame
        rankings_df = rankings_df.rename(columns={
                    'Rank': 'rank',
                    'Nation': 'nation',
                    'Confederation': 'confederation',
                    'Points': 'points',
                    'Date': 'date'
                })
        
        # Additional data cleaning steps
        results_df['outcome'] = results_df.apply(
            lambda x: 'H' if x['home_score'] > x['away_score'] else ('A' if x['home_score'] < x['away_score'] else 'D'),
            axis=1,
        )
        results_df['winning_team'] = results_df.apply(
            lambda x: x['home_team']
            if x['home_score'] > x['away_score'] else (x['away_team'] if x['home_score'] < x['away_score'] else np.nan),
            axis=1,
        )
        results_df['losing_team'] = results_df.apply(
            lambda x: x['away_team']
            if x['home_score'] > x['away_score'] else (x['home_team'] if x['home_score'] < x['away_score'] else np.nan),
            axis=1,
        )
        results_df['total_goals'] = results_df['home_score'] + results_df['away_score']
        results_df['year'] = pd.DatetimeIndex(results_df['date']).year
        results_df['decade'] = results_df['year'] - results_df['year'] % 10
    
        return results_df, rankings_df, team_names_df
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return None, None

if __name__ == "__main__":
    results_df, rankings_df, team_names_df = load_data()

    if results_df is not None:
        print("Results DataFrame:")
        print(results_df.head())
        file_path = "../data/processed/cleaned_results_data.csv"
        results_df.to_csv(file_path, index=False)
        print("Cleaned Results DataFrame exported to 'cleaned_results_data.csv'.")
    else:
        print("Results DataFrame is empty or not available.")
    if rankings_df is not None:
        print("\nRankings DataFrame:")
        print(rankings_df.head())
        file_path = "../data/processed/cleaned_rankings_data.csv"
        rankings_df.to_csv(file_path, index=False)
        print("Cleaned rankings Dataframe exported to 'cleaned_rankings_data.csv'.")
    else:
        print("Rankings DataFrame is empty or not available.")
    if team_names_df is not None:
        print("\nTeam Names DataFrame:")
        print(team_names_df.head())
        file_path = "../data/processed/team_names_data.csv"
        team_names_df.to_csv(file_path, index=False)
        print("Cleaned Team Names Dataframe exported to 'team_names_data.csv'.")
    else:
        print("Team Names DataFrame is empty or not available.")


