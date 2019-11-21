import pandas as pd
import numpy as np
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

# Sets first row as column labels
def _set_header(df: pd.DataFrame):
    df.rename(columns=df.iloc[0], inplace=True)
    df.drop(index=df.index[0], inplace=True)

def _set_dtypes(df: pd.DataFrame):
    df['Price'] = pd.to_numeric(df['Price'], downcast='float')
    df['PriceUpdatedDate'] = (
            pd.to_datetime(df['PriceUpdatedDate'], format='%d/%m/%Y %I:%M:%S %p'))
    return df

def _clean(df: pd.DataFrame) -> pd.DataFrame:
    # Drop row all nans e.g. some sheets have whitespace at start of file
    df.dropna(how='all', inplace=True)
    _set_header(df)

    # Data from excel sheets sometimes has empty space where there is replication,
    # but with FuelCode, PriceUpdatedDate, Price intact
    def interpolate(col: pd.Series) -> pd.Series:
        if (col.name != 'FuelCode'
        and col.name != 'PriceUpdatedDate'
        and col.name != 'Price'):
            col = col.interpolate(method='pad', limit_direction='forward')
        return col
    df = df.apply(interpolate, axis=0)
    # Clean up any rows that haven't been interpolated
    df.dropna(how='any', inplace=True)

    _set_dtypes(df)

    return df

# Returns data from monthly excel file at url
def _read_month(url: str, name: str) -> pd.DataFrame:
    date = _extract_date(name)
    FORMAT_CHANGE_DATE = datetime(2017, day=1, month=7)
    args = {'io': url, 'header': None}
    if date < FORMAT_CHANGE_DATE:
        new_df = pd.read_excel(**args)
    # From 7/2017 format changed to add a title in 1st row
    else:
        args['skiprows'] = 1
        new_df = pd.read_excel(**args)

    return _clean(new_df)

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
