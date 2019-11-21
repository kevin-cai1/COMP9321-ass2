import pandas as pd
from sklearn.preprocessing import scale


df = pd.read_excel("fuel_data/price_history_checks_oct2019.xlsx", skiprows=2)

df2 = df.query('1000 <= Postcode <= 2249')
df3 = df.query('2760 <= Postcode <= 2770')

df2 = df2.append(df3)
print(df2)

station_list = df2.ServiceStationName.unique()
suburb_list = df2.Suburb.unique()

print(station_list[:20])
print(len(station_list))

print(suburb_list[:20])
print(len(suburb_list))

files = 0
for station in station_list:
    if isinstance(station, str):
        print(station)
        temp_df = df.query('ServiceStationName == @station')
        fuel_types = temp_df.FuelCode.unique()
        for fuel in fuel_types:
        #    fuel_df = temp_df.query('FuelCode == @fuel')
        #    df = fuel_df[['PriceUpdatedDate', 'Price']]

        #    price_x = df.drop('Price', axis=1).values
        #    price_y = df['Price'].values

            #price_x = scale(price_x)

            #linear_model = LinearRegression()
            #linear_model.fit(price_x, price_y)

            filename = station + "_" + str(fuel) + ".sav"
            files+= 1
            print(filename)
            #filename = 'model.sav'  # change filename to reflect current 
            #pickle.dump(linear_model, open(filename, 'wb'))
print(files)



#df2 = df['Postcode'].between(1000, 2249) & df['Postcode'].between(2760, 2770)

#print(df2)