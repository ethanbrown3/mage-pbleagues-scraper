from toolz.curried import map, pipe, first
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


BASE_URL = "https://pbleagues.com"
FORFEIT_ACCEPTED = 'A'
FORFEITED = 'F'


def scrape_match_data(event_id):
    url = f"{BASE_URL}/event/{event_id}"
    resource = "/scores"
    response = requests.get(url + resource)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all divisions
    divisions = soup.find_all('div', class_='division item')

    match_data = []
    
    # Loop through each division
    for division in divisions:
        division_name = division.find('h3').text.strip()

        # Skip divisions that do not have "X-Ball" in the title
        if "X-Ball" not in division_name:
            continue

        # Find all rounds in the division
        rounds = division.select('div.tab-pane.fade, div.tab-pane.fade.in.active')
        # print(rounds)
        # Loop through each round
        for round_div in rounds:
            # print(round_div)
            if 'all' in round_div.get('id', ''):
                continue
            round_name = round_div.find('h4', class_='hidden-title').text.strip()
            # print(round_name)

            # Find all matches in the round
            matches = round_div.find_all('tr')[1:]  # Skip the header row
            # print(len(matches))
            # Loop through each match
            for match_row in matches:
                for match in match_row.find_all('td', align='CENTER'):
                    if not match.find('a'):
                        continue
                    team_name = match.find('a')['title']
                    score = match.text.strip()
                    match_link = match.find('a', href=True)['href']

                    # Split the team names and scores
                    team1_name, team2_name = team_name.split(' vs. ')
                    if score == FORFEIT_ACCEPTED:
                        score1, score2 = 1, 0
                    elif score == FORFEITED:
                        score1, score2 = 0, 1
                    else:
                        score1, score2 = score.split('-')

                    # Append the match data to the match_data list
                    match_data.append([event_id, division_name, round_name, team1_name,
                                    team2_name, score1, score2, match_link])

    # Create pandas DataFrame from the data
    df_match = DataFrame(match_data, columns=['event_id', 'division', 'round',
                            'team1', 'team2', 'score1', 'score2', 'match_link'])
    print(f'event_id: {event_id}::{len(df_match)} matches')
    return df_match


@data_loader
def load_data(data: DataFrame, *args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    return pipe(data,
                lambda x: x['event_id'].tolist(),
                map(scrape_match_data),
                list,
                pd.concat)


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'


if __name__ == '__main__':
    event_df = DataFrame({'event_id': [
        8150, 8098, 8016, 7927, 7751, 7648, 7649, 7647, 7604, 7537, 7349, 7286, 7297, 7250, 7170, 7109, 6990, 6726,
        6251, 6250, 6249, 6248, 6273, 5978, 5976, 5969, 5902, 5760, 5585, 5524, 5522, 5460, 5174, 4981, 4885, 4844,
        4770, 4661, 4564, 4310, 4238, 4145]})
    load_data(event_df)
