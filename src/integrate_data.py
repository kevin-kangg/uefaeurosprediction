"""
Integrates all the data into a format that can be easily analyzed
This will probably take the form of merging (joining) several Pandas
DataFrames, or issuing SQL queries over tables in a relational DB.

Author: Kevin Kang
"""
import pandas as pd
import time

def load_data():
    try:
        # Load the CSV files into pandas DataFrames
        cleaned_results_df = pd.read_csv('../data/processed/cleaned_results_data.csv')
        # Shootouts file is already clean
        shootouts_df = pd.read_csv('../data/raw/shootouts.csv')
        rankings_df = pd.read_csv('../data/processed/cleaned_rankings_data.csv')
        
        # Merge results and shootouts DataFrames
        merged_results_df = cleaned_results_df.merge(shootouts_df, how='left', on=['home_team', 'away_team', 'date'])
        merged_results_df['winning_team'] = merged_results_df.apply(
            lambda x: x['winner'] if not pd.isnull(x['winner']) and pd.isnull(x['winning_team']) else x['winning_team'],
            axis=1,
        )
        merged_results_df['losing_team'] = merged_results_df.apply(
            lambda x: x['home_team'] if x['winning_team'] == x['away_team'] and x['outcome'] == 'D' else x['away_team']
            if x['winning_team'] == x['home_team'] and x['outcome'] == 'D' else x['losing_team'],
            axis=1,
        )
        merged_results_df.drop(columns=['winner'], inplace=True)

        # Convert the 'date' column to datetime format
        merged_results_df['date'] = pd.to_datetime(merged_results_df['date'])

        # Filter the merged_data DataFrame
        filtered_results_df = merged_results_df[merged_results_df['date'] >= '2009-09-02']

        return filtered_results_df, rankings_df
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return None, None
    
def find_closest_ranking_date(match_date, ranking_dates):
    closest_date = min(ranking_dates, key=lambda x: abs(x - match_date))
    return closest_date

def calculate_proportion(row, threshold_rank):
    home_rank = row['home_rank']
    away_rank = row['away_rank']
    
    # Check for null values
    if pd.isna(home_rank) or pd.isna(away_rank):
        return False
    
    if home_rank <= threshold_rank or away_rank <= threshold_rank:
        return True
    else:
        return False

if __name__ == "__main__":
    
    
    # Call the load_data function to load the data
    filtered_results_df, rankings_df = load_data()
    
    if filtered_results_df is not None and rankings_df is not None:
        # Convert the 'date' columns to datetime format
        filtered_results_df['date'] = pd.to_datetime(filtered_results_df['date'])
        rankings_df['date'] = pd.to_datetime(rankings_df['date'])
        
        # Find the closest ranking date for each match date
        filtered_results_df['closest_ranking_date'] = filtered_results_df['date'].apply(
            lambda x: find_closest_ranking_date(x, rankings_df['date'])
        )

        # Merge the datasets based on the closest ranking dates
        merged_data = pd.merge(filtered_results_df, rankings_df, left_on=['home_team', 'closest_ranking_date'], right_on=['nation', 'date'], how='left')
        merged_data.rename(columns={'rank': 'home_rank'}, inplace=True)
        merged_data = pd.merge(merged_data, rankings_df, left_on=['away_team', 'closest_ranking_date'], right_on=['nation', 'date'], how='left')
        merged_data.rename(columns={'rank': 'away_rank'}, inplace=True)

        # Reorder columns to move the 'date' column to the first position
        merged_data = merged_data[['date_x'] + [col for col in merged_data.columns if col != 'date_x']]
        merged_data.rename(columns={'date_x': 'date'}, inplace=True)

        # Drop  unnecessary columns
        merged_data.drop(columns=['closest_ranking_date', 'date_y'], inplace=True)

        # Define High-Ranking Teams
        threshold_rank = merged_data['home_rank'].quantile(0.1)  # Example: Top 10%

        # Apply the calculate_proportion function to create a new column indicating high-ranking teams
        merged_data['high_ranking'] = merged_data.apply(lambda row: calculate_proportion(row, threshold_rank), axis=1)

        # Display basic information about the filtered DataFrame
        print("Integrated DataFrame:")
        print(merged_data.head())

        # Export to a CSV file
        merged_data.to_csv('../data/processed/integrated_merged_data.csv', index=False)
        print("Filtered Merged DataFrame exported to 'integrated_merged_data.csv'.")
        
    else:
        print("Error: Data loading failed.")
