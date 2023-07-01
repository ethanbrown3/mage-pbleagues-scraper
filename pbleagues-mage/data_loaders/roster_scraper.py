import requests
from bs4 import BeautifulSoup
import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


BASE_URL = "https://pbleagues.com"


def scrape_roster_data(event_id):
    url = f"{BASE_URL}/event/{event_id}/scores"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all divisions
    divisions = soup.find_all('div', class_='division item')

    roster_data = []

    # Loop through each division
    for division in divisions:
        division_name = division.find('h3').text.strip()

        # Skip divisions that do not have "X-Ball" in the title
        if "X-Ball" not in division_name:
            continue

        # Find all team names in the division
        rosters = division.find_all('td', class_=['grey teamName', 'white teamName'])

        # Loop through each team
        for roster in rosters:
            team_name = roster.text.strip()
            roster_link = roster.find('a', href=True)['href']

            # Append the team data to the team_data list
            roster_data.append([division_name, team_name, roster_link])

    # Create pandas DataFrame from the data
    df_roster = pd.DataFrame(roster_data, columns=['Division', 'Team', 'Team Link'])

    return df_roster


@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your data loading logic here

    return {}


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'


'<td align="CENTER" class="lred"><a href="/cgi-bin/showgame.cgi?EID=7751&amp;size=255&amp;round=0&amp;GID=205" title="Wolves Blackout  vs. Rushers">F</a></td>'
