import pandas as pd
from sklearn.preprocessing import scale


df4 = pd.read_excel("fuel_data/price_history_checks_oct2019.xlsx", skiprows=2)
df3 = pd.read_excel("fuel_data/price_history_checks_sep2019.xlsx", skiprows=2)
df1 = pd.read_excel("fuel_data/service-station-price-history-jul-2019.xlsx", skiprows=2)
df2 = pd.read_excel("fuel_data/service-station-price-history-aug-2019.xlsx", skiprows=2)

df = df1.append(df2, ignore_index=True)
df = df.append(df3, ignore_index=True)
df = df.append(df4, ignore_index=True)

df = df.query('ServiceStationName == "Metro Fuel Marrickville"')

df = df.query('FuelCode == "E10"')

print(df)

df.to_excel('marrickville_4_months.xlsx')
#df2 = df.query('1000 <= Postcode <= 2249')
#df3 = df.query('2760 <= Postcode <= 2770')

#df2 = df2.append(df3)

#station_list = df2.ServiceStationName.unique()
#suburb_list = df2.Suburb.unique()

#data = []
#index = 0
#for station in station_list:
#    station_row = {'ServiceStationCode': index, 'ServiceStationName': station}
#    index += 1
#    data.append(station_row)
#
#station_df = pd.DataFrame(data)

#print(station_df)

#station_df.to_csv('station_code_mapping.csv',index=False)