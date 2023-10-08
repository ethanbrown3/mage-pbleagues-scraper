from datetime import datetime
import re
import requests

from bs4 import BeautifulSoup
import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


BASE_URL = "https://pbleagues.com"


def parse_date_range(date_range):
    parts = re.split(' *- *', date_range)
    if len(parts) == 2:
        start, end = parts
        end_split = end.split(', ')
        if len(end_split) != 2:
            end_day = end_split[0]
            year = datetime.now().year
        else:
            end_day, year = end_split
        start_month, start_day = re.split(' +', start)
        if end_day[0].isalpha():
            end_month, end_day = start_month, start_day = re.split(' +', end_day)
        else:
            end_month = start_month
    else:
        raise ValueError(f'{date_range} Invalid date range format')

    start_date = datetime.strptime(f'{start_month} {start_day} {year}', '%B %d %Y')
    end_date = datetime.strptime(f'{end_month} {end_day} {year}', '%B %d %Y')

    return start_date, end_date


def scrape_events(league_id):
    # URL of the league page
    url = f"{BASE_URL}/leagues/{league_id}"

    # Send an HTTP GET request and retrieve the HTML content
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the table containing the events
    events_table = soup.find("table", class_="table-condensed")

    # Extract the event data
    events = []
    for event_row in events_table.find_all("tr"):
        columns = event_row.find_all("td")
        if len(columns) == 2:
            event_link = columns[1].find("a")
            event_name = event_link.text.strip()
            if 'practice' in event_name.lower():
                continue
            date = columns[0].text.strip()
            event_href = event_link["href"]
            event_id = int(event_href.rsplit('/', 1)[-1])
            try:
                start_date, end_date = parse_date_range(date)
            except ValueError:
                print(f'Event: {event_name} Invalid date range {date}')
            event = {
                "event_id": event_id,
                "date_string": date,
                "start_date": start_date,
                "end_date": end_date,
                "name": event_name,
                "link": f"{BASE_URL}{event_href}"
            }
            events.append(event)

    return events


def create_events_dataframe(events):
    df = pd.DataFrame(events)
    return df


@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # League ID
    league_id = kwargs['league_id']

    # Scrape the events
    scraped_events = scrape_events(league_id)

    # Create a DataFrame from the scraped events
    events_dataframe = create_events_dataframe(scraped_events)

    return events_dataframe


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
