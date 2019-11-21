import pandas as pd
import numpy as np
import datetime
import requests

# Extracts date from data's name.
# name format: Fuelcheck Price History MONTH YEAR[.xlsx]
def _extract_date(name: str) -> datetime.date:
    # some names have .xlsx in them
    name = name.strip()
    split = name.partition('.xlsx')[0].split(' ')
    if len(split) < 2:
        raise ValueError('Invalid name: {}'.format(name))
    month = split[-2]
    year = split[-1]

    try:
        return datetime.datetime.strptime(month[:3] + '-' + year, '%b-%Y').date()
    except ValueError:
        raise ValueError('Invalid name: {}'.format(name))

# Sets first row as column labels
def _set_header(df: pd.DataFrame) -> pd.DataFrame:
    df.rename(columns=df.iloc[0], inplace=True)
    df.drop(index=df.index[0], inplace=True)
    df.columns = df.columns.str.strip()
    return df

def _set_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    df['Price'] = pd.to_numeric(df['Price'], downcast='float')
    df['PriceUpdatedDate'] = (
            pd.to_datetime(df['PriceUpdatedDate'], format='%d/%m/%Y %I:%M:%S %p'))
    return df

def _clean(df: pd.DataFrame) -> pd.DataFrame:
    # Some sheets have 3 'valid' NaNs (8 cols total) that
    # must be inferred i.e. FuelCode, PriceUpdatedDate, Price
    # Some sheets have useless rows e.g. at start
    df.dropna(thresh=3, inplace=True)
    df = _set_header(df)

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

    df = _set_dtypes(df)

    return df

# Returns data from monthly excel file at url
def _read_month(url: str) -> pd.DataFrame:
    new_df = pd.read_excel(io=url, header=None)
    return _clean(new_df)

# Returns combined monthly price histories starting from 'start' and until
# 'end', both inclusive
def read(start: datetime.date, end: datetime.date) -> pd.DataFrame:
    META_URL = 'https://data.nsw.gov.au/data/api/3/action/package_show?id=a97a46fc-2bdd-4b90-ac7f-0cb1e8d7ac3b'
    resp = requests.get(META_URL)
    resp.raise_for_status()

    resources = (resp.json())['result']['resources']
    DATA_OFFSET = 4
    df = pd.DataFrame()
    for resource in resources[DATA_OFFSET:]:
        date = _extract_date(resource['name'])
        if (date >= start
        and date <= end):
            df = df.append(_read_month(resource['url'])
                           , ignore_index=True
                           , sort=True)

    return df

if __name__ == "__main__":
    df = read(start=datetime.date(2019, 10, 1), end=datetime.date(2019, 10, 1))
    print(df.head(5).to_string())
    print(df.tail(5).to_string())
    print('types: {}'.format(df.dtypes))
