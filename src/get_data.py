"""
Download the data and store it in the data/raw folder

Author: Kevin Kang
"""

import requests
from bs4 import BeautifulSoup
import csv
import os

def scrape_team_names(base_url, groups):
    """
    Scrape team names for UEFA Euro 2024 groups A to F.

    Args:
        base_url (str): The base URL of the UEFA Euro 2024 group pages.
        groups (list): A list of strings representing the groups (e.g., ["A", "B", "C", "D", "E", "F"]).

    Returns:
        dict: A dictionary containing the group names as keys and the corresponding team names as values.
    """
    team_names_dict = {}
    
    for group in groups:
        # Construct the URL for the current group
        url = base_url + group
        
        try:
            # Send a GET request to the URL
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content
                soup = BeautifulSoup(response.content, "html.parser")

                # Find the <b> tag containing the group information
                group_b_tag = soup.find("b")

                # Extract the team names from the <b> tag
                team_names = [a_tag.get_text() for a_tag in group_b_tag.find_all_next("a")]

                # Store the extracted team names in the dictionary
                team_names_dict[group] = team_names[2:6]
            else:
                print(f"Failed to retrieve data for Group {group}. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred while processing Group {group}: {e}")

    return team_names_dict

def save_to_csv(data, output_folder):
    """
    Save the scraped data to a CSV file.

    Args:
        data (dict): A dictionary containing the data to be saved.
        output_folder (str): The folder path where the CSV file will be saved.
    """
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "team_names.csv")
    
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Group", "Team 1", "Team 2", "Team 3", "Team 4"])
        for group, team_names in data.items():
            writer.writerow([group] + team_names)

if __name__ == "__main__":
    # Base URL of the UEFA Euro 2024 group pages
    base_url = "https://en.wikipedia.org/wiki/UEFA_Euro_2024_Group_"

    # Groups A to F
    groups = ["A", "B", "C", "D", "E", "F"]

    # Scrape team names for groups A to F
    team_names_dict = scrape_team_names(base_url, groups)

    # Specify the output folder relative to the current script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(script_dir, "..", "data", "raw")

    # Save the scraped team names to a CSV file
    save_to_csv(team_names_dict, output_folder)

    print("Team names saved to CSV file successfully.")


def scrape_transfermarkt_world_ranking(date):
    base_url = f"https://www.transfermarkt.us/statistik/weltrangliste/statistik/stat/datum/{date}/plus/0/galerie/0/page/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        data = []
        page = 1
        while True:
            url = f"{base_url}{page}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the rankings table
            rankings_table = soup.find('table', class_='items')
            if rankings_table:
                # Extract rows from the table
                rows = rankings_table.find_all('tr')
                for row in rows:
                    # Extract columns from each row
                    columns = row.find_all('td')
                    if len(columns) >= 3:  # Ensure the row has at least 3 columns
                        rank = columns[0].text.strip()
                        nation = columns[1].text.strip()
                        confederation = columns[2].text.strip()
                        points = columns[3].text.strip()
                        data.append((rank, nation, confederation, points, date))
                
                # Check if there are more pages
                next_page_link = soup.find('a', class_='tm-pagination__link', title='Go to the next page')
                if not next_page_link:
                    break  # Exit the loop if there are no more pages
                page += 1
            else:
                print("Rankings table not found.")
                return None
        return data
    except requests.exceptions.RequestException as e:
        print("Failed to fetch the page:", e)
        return None

def save_to_csv(data, filename):
    # Get the parent directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the CSV file
    file_path = os.path.join(script_dir, filename)
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Rank', 'Nation', 'Confederation', 'Points', 'Date'])
        writer.writerows(data)

def scrape_all_dates():
    all_data = []
    url = "https://www.transfermarkt.us/statistik/weltrangliste/statistik/stat/plus/0/galerie/0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the dropdown menu containing dates
        date_select = soup.find('select', attrs={'name': 'datum'})
        if date_select:
            # Extract date options
            date_options = date_select.find_all('option')
            for option in date_options:
                date_value = option.get('value')
                if date_value and date_value != '2024-04-04':  # Exclude April 4, 2024
                    print(f"Scraping data for {option.text}...")
                    rankings_data = scrape_transfermarkt_world_ranking(date_value)
                    if rankings_data:
                        all_data.extend(rankings_data)
                    else:
                        print("No rankings data found.")
        else:
            print("Date dropdown not found.")
        
        # Save all data to a single CSV file
        save_to_csv(all_data, "../data/raw/all_rankings_data.csv")
        print("All data saved to ../data/raw/all_rankings_data.csv")
    except requests.exceptions.RequestException as e:
        print("Failed to fetch the page:", e)

# Scrape data for all dates and save to a single CSV file
scrape_all_dates()


# Define the base URL where the CSV files are located
base_url = 'https://raw.githubusercontent.com/martj42/international_results/master/'

# List of CSV files to download
csv_files = ['results.csv', 'goalscorers.csv', 'shootouts.csv']

# Define the directory paths
parent_directory = os.path.dirname(os.path.abspath(__file__))  # Get the parent directory of the current script
data_directory = os.path.join(parent_directory, '..', 'data', 'raw')  # Navigate to the data directory in the parent directory

# Check if the data directory exists, create it if not
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# Download and save each CSV file
for csv_file in csv_files:
    # Construct the URL for the current CSV file
    url = base_url + csv_file
    
    # Send a GET request to download the CSV file
    res = requests.get(url, allow_redirects=True)
    
    # Define the path for the CSV file in the data directory
    csv_file_path = os.path.join(data_directory, csv_file)
    
    # Write the content of the CSV file to the specified path
    with open(csv_file_path, 'wb') as file:
        file.write(res.content)

# Now the 'results.csv', 'goalscorers.csv', and 'shootouts.csv' files are saved in the 'data' directory above the current script directory