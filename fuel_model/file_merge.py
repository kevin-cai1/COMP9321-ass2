import pandas as pd
import re
import datetime

# Extracts date from xlsx file in url.
# xlsx name format: service-station-price-history-MONTH-YEAR.xlsx
def _extract_date(url: str) -> datetime:
    filename = url.split('/')[-1].replace('.xlsx', '')
    filename_split = filename.split('-')
    if len(filename_split) < 2:
        raise ValueError('Invalid URL format: {}'.format(str))
    date = filename_split[-2] + '-' + filename_split[-1]

    try:
        return datetime.datetime.strptime(date, '%B-%Y')
    except ValueError:
        raise ValueError('Invalid URL format: {}'.format(str))

# Returns data from excel file at url
def read_price_history(url: str) -> pd.DataFrame:
    FORMAT_CHANGE_DATE = datetime.datetime(2017, day=1, month=7)
    if _extract_date(url) < FORMAT_CHANGE_DATE:
        new_df = pd.read_excel(url)
    # From 7/2017 format changed to add a title in 1st row
    else:
        new_df = pd.read_excel(url, skiprows=1)

    return new_df 

if __name__ == "__main__":
    print("before format change...")
    df = read_price_history('https://data.nsw.gov.au/data/dataset/a97a46fc-2bdd-4b90-ac7f-0cb1e8d7ac3b/resource/dba9405e-ad7e-4280-b994-041485db0e88/download/service-station-price-history-june-2017.xlsx')
    print(df.head(5).to_string())

    print("after format change...")
    df = read_price_history('https://data.nsw.gov.au/data/dataset/a97a46fc-2bdd-4b90-ac7f-0cb1e8d7ac3b/resource/d59adf5e-bcf6-4b0c-82a6-41ac9ec9162a/download/service-station-price-history-july-2017.xlsx')
    print(df.head(5).to_string())

#df1 = pd.read_excel("service-station-price-history-may-2017.xlsx")
#df2 = pd.read_excel("service-station-price-history-june-2017.xlsx")
#df3 = pd.read_excel("service-station-price-history-july-2017.xlsx", skiprows=1)
#df4 = pd.read_excel("service-station-price-history-august-2017.xlsx", skiprows=1)
#df5 = pd.read_excel("service-station-price-history-september-2017.xlsx", skiprows=1)
#
#df = df1.append(df2, ignore_index=True)
#df = df.append(df3, ignore_index=True)
#df = df.append(df4, ignore_index=True)
#df = df.append(df5, ignore_index=True)
#
#df = df.query('FuelCode == "E10"')
#df = df.query('ServiceStationName =="7-Eleven Artarmon"')
#
#df1 = df[['PriceUpdatedDate', 'Price']]
#
#df.to_excel('fuel_data_may-september_2017.xlsx')
#print(df)
