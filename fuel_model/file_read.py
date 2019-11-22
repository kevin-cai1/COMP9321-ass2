import pandas as pd
from sklearn.preprocessing import scale


df = pd.read_excel("fuel_data/price_history_checks_oct2019.xlsx", skiprows=2)

df2 = df.query('1000 <= Postcode <= 2249')
df3 = df.query('2760 <= Postcode <= 2770')

df2 = df2.append(df3)

station_list = df2.ServiceStationName.unique()
suburb_list = df2.Suburb.unique()

data = []
index = 0
for station in station_list:
    station_row = {'ServiceStationCode': index, 'ServiceStationName': station}
    index += 1
    data.append(station_row)

station_df = pd.DataFrame(data)

print(station_df)

station_df.to_csv('station_code_mapping.csv',index=False)