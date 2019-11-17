import pandas as pd

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