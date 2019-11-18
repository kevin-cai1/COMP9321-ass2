import pandas as pd
import re
import datetime

# Extracts date from xlsx file in url.
# xlsx name format: service-station-price-history-MONTH-YEAR.xlsx
def _extract_date(url: str) -> datetime:
    filename = url.split('/')[-1].replace('.xlsx', '')
    filename_split = filename.split('-')
    if len(filename_split < 2):
        raise ValueError('Invalid URL format: {}'.format(str))
    date = filename_split[-2] + '-' + filename_split[-1]

    try:
        return datetime.datetime.strptime(date, '%B-%Y')
    except ValueError:
        raise ValueError('Invalid URL format: {}'.format(str))

#def append_data(df: pd.DataFrame, url: str) -> pd.DataFrame:
#
#    new = pd.read_excel(url)

df1 = pd.read_excel("service-station-price-history-may-2017.xlsx")
df2 = pd.read_excel("service-station-price-history-june-2017.xlsx")
df3 = pd.read_excel("service-station-price-history-july-2017.xlsx", skiprows=1)
df4 = pd.read_excel("service-station-price-history-august-2017.xlsx", skiprows=1)
df5 = pd.read_excel("service-station-price-history-september-2017.xlsx", skiprows=1)

df = df1.append(df2, ignore_index=True)
df = df.append(df3, ignore_index=True)
df = df.append(df4, ignore_index=True)
df = df.append(df5, ignore_index=True)

df = df.query('FuelCode == "E10"')
df = df.query('ServiceStationName =="7-Eleven Artarmon"')

df1 = df[['PriceUpdatedDate', 'Price']]

df.to_excel('fuel_data_may-september_2017.xlsx')
print(df)
