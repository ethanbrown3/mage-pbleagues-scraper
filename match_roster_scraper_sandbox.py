import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://pbleagues.com/event/8098/scores"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all divisions
divisions = soup.find_all('div', class_='division item')

match_data = []
team_data = []

# Loop through each division
for division in divisions:
    division_name = division.find('h3').text.strip()

    # Skip divisions that do not have "X-Ball" in the title
    if "X-Ball" not in division_name:
        continue

    # Find all rounds in the division
    rounds = division.find_all('div', class_='tab-pane fade')

    # Loop through each round
    for round_div in rounds:
        round_name = round_div.find('h4', class_='hidden-title').text.strip()

        # Find all matches in the round
        matches = round_div.find_all('tr')[1:]  # Skip the header row

        # Loop through each match
        for match in matches:
            lgreen = match.find('td', class_=['lgreen', 'lred'])
            team_name = lgreen.find('a')['title']
            score = lgreen.text.strip()
            match_link = lgreen.find('a', href=True)['href']

            # Split the team names and scores
            team1_name, team2_name = team_name.split(' vs. ')
            score1, score2 = score.split('-')

            # Append the match data to the match_data list
            match_data.append([division_name, round_name, team1_name, team2_name, score1, score2, match_link])

    # Find all team names in the division
    teams = division.find_all('td', class_=['grey teamName', 'white teamName'])

    # Loop through each team
    for team in teams:
        team_name = team.text.strip()
        team_link = team.find('a', href=True)['href']

        # Append the team data to the team_data list
        team_data.append([division_name, team_name, team_link])

# Create pandas DataFrames from the data
df_match = pd.DataFrame(match_data, columns=['Division', 'Round', 'Team1', 'Team2', 'Score1', 'Score2', 'Match Link'])
df_team = pd.DataFrame(team_data, columns=['Division', 'Team', 'Team Link'])

print(df_match)
print(df_team)
