import pandas as pd
from datetime import datetime
import requests

# Extracts date from data's name.
# name format: Fuelcheck Price History MONTH YEAR[.xlsx]
def _extract_date(name: str) -> datetime:
    # some names have .xlsx in them
    split = name.partition('.xlsx')[0].split(' ')
    if len(split) < 2:
        raise ValueError('Invalid name: {}'.format(name))
    month = split[-2][:3]
    year = split[-1]

    try:
        return datetime.strptime(month + '-' + year, '%b-%Y')
    except ValueError:
        raise ValueError('Invalid name: {}'.format(name))

def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how='all')
    df = df.interpolate(method='pad')
    return df

# Returns data from monthly excel file at url
def _read_month(url: str, name: str) -> pd.DataFrame:
    FORMAT_CHANGE_DATE = datetime(2017, day=1, month=7)
    if _extract_date(name) < FORMAT_CHANGE_DATE:
        new_df = pd.read_excel(url)
    # From 7/2017 format changed to add a title in 1st row
    # TODO: check format change where 2nd row is empty
    else:
        new_df = pd.read_excel(url, skiprows=1)

    #return _clean(new_df)
    return new_df

# Returns combined monthly price histories
def read() -> pd.DataFrame:
    URL = 'https://data.nsw.gov.au/data/api/3/action/package_show?id=a97a46fc-2bdd-4b90-ac7f-0cb1e8d7ac3b'
    resp = requests.get(URL)
    resp.raise_for_status()

    resources = (resp.json())['result']['resources']
    DATA_OFFSET = 4
    df = _read_month(resources[DATA_OFFSET]['url']
                     , resources[DATA_OFFSET]['name'])
    for resource in resources[DATA_OFFSET + 1:]:
        df = df.append(_read_month(resource['url'], resource['name'])
                       , ignore_index=True
                       , sort=True)

    return df

if __name__ == "__main__":
    #df = read()
    df = _read_month('https://data.nsw.gov.au/data/dataset/a97a46fc-2bdd-4b90-ac7f-0cb1e8d7ac3b/resource/efcbe322-d35f-4fba-8f8b-b073035cfad5/download/price_history_checks_oct2019.xlsx', 'FuelCheck Price History October 2019')
    print(df.head(5).to_string())
    print(df.tail(5).to_string())
    print('types: {}'.format(df.dtypes))
