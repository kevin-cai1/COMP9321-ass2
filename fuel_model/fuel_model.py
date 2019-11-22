import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures, scale
from sklearn.pipeline import make_pipeline
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error
import numpy as np
from datetime import datetime


# return predicted price for a given date, fuel station and fuel type
def get_prediction(date, fuel_station, fuel_type):
    # load the model specified by fuel station and fuel type
    # filename = {some standardised format with specific params}
    # loaded_model = pickle.load(open(filename, 'rb'))

    # result = loaded.model.predict(date)

    # print(result)
    #return result
    pass



def load_price(df, split_percentage):
    df = shuffle(df)

    price_x = df.drop('Price', axis=1).values
    price_y = df['Price'].values

    price_x = scale(price_x)

    split_point = int(len(price_x) * split_percentage)
    price_x_train = price_x[:split_point]
    price_y_train = price_y[:split_point]
    price_x_test = price_x[split_point:]
    price_y_test = price_y[split_point:]

    return price_x_train, price_y_train, price_x_test, price_y_test

    

def normalize_data(df): 
    df2 = df.query('1000 <= Postcode <= 2249')
    df3 = df.query('2760 <= Postcode <= 2770')

    metro_df = df2.append(df3, ignore_index=True)  # extracts just listings within the sydney metro area

    df1 = metro_df[['ServiceStationName', 'FuelCode', 'PriceUpdatedDate', 'Price']]

    df1['PriceUpdatedDate'] = df1['PriceUpdatedDate'].apply(extract_date)   # format date to remove time
        
    return df1 
    
def extract_date(x):
    x = str(x).split(' ')
    x = x[0]
    return x

def init_model():
    df = pd.read_excel("fuel_data/price_history_checks_oct2019.xlsx", skiprows=2)   # load dataset

    df = normalize_data(df) # format data for necessary rows and columns

    fuel_list = ["E10", "U91", "P95", "P98"]  # list of supported fuel types

    for fuel in fuel_list:
        fuel_df = df.query('FuelCode == @fuel')

        print(fuel_df)
        fuel_model = load_model(df)
        filename = "fuel_model_" + fuel + ".sav"
        print(filename)
    
        pickle.dump(fuel_model, open(filename, 'wb'))    # save model to memory

def load_model(df):
    model_x = df[['ServiceStationName', 'PriceUpdatedDate']].values     # features that dictate prediction
    model_y = df['Price'].values                                        # feature to predict
   
    model = LinearRegression()
    model.fit(model_x, model_y)

    return model

if __name__ == "__main__":
    init_model()