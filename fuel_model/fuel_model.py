import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures, scale
from sklearn.pipeline import make_pipeline
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error
import numpy as np
import datetime
import pickle



# return predicted price for a given date, fuel station and fuel type
# date is a value of datetime.date
# fuel_station_code is a code referencing a particular station (code can be found from station_code_mapping.csv)
#fuel_type is a fuel type of either ["E10", "U91", "P95", "P98"] 
def get_prediction(date, fuel_station_code, fuel_type):
    # load the model specified by fuel type
    filename = './models/fuel_model_' + fuel_type + ".sav" 
    loaded_model = pickle.load(open(filename, 'rb'))

    #data going into model should be of type np.array(fuel_station_code, date) with date being ordinal date
    data = np.array([[fuel_station_code, date.toordinal()]])
    result = loaded_model.predict(data)

    print(result)
    return result


# splits data into train and test segments
def load_price(df, split_percentage):
    df = shuffle(df)

    price_x = df[['ServiceStationCode', 'PriceUpdatedDate']].values     # features that dictate prediction
    price_y = df['Price'].values  

    split_point = int(len(price_x) * split_percentage)
    price_x_train = price_x[:split_point]
    price_y_train = price_y[:split_point]
    price_x_test = price_x[split_point:]
    price_y_test = price_y[split_point:]

    return price_x_train, price_y_train, price_x_test, price_y_test

    
# formats dataframe and removes unnecessary columns
def normalize_data(df): 
    df2 = df.query('1000 <= Postcode <= 2249')
    df3 = df.query('2760 <= Postcode <= 2770')

    metro_df = df2.append(df3, ignore_index=True)  # extracts just listings within the sydney metro area

    df1 = metro_df[['ServiceStationName', 'FuelCode', 'PriceUpdatedDate', 'Price']]
        
    map_df = pd.read_csv("station_code_mapping.csv")

    df1 = df1.dropna()  # remove nan rows
        
    df1['PriceUpdatedDate'] = df1['PriceUpdatedDate'].apply(extract_date)   # format date to be ordinal date

    new_df = pd.merge(map_df, df1, how='inner', on='ServiceStationName')    # add service station code for station name
    return_df = new_df[['ServiceStationCode', 'FuelCode', 'PriceUpdatedDate', 'Price']]

    return return_df 
    
# converts date from string into ordinal date
def extract_date(x):
    x = str(x).split(' ')   # gets just the date
    x = x[0]
    date = x.split('/')
    date_date = datetime.date(int(date[2]), int(date[1]), int(date[0])) #date(year, month, day)
    return date_date.toordinal()

# instantiates and saves the training models into fuel_model/models
def init_model():
    df = pd.read_excel("fuel_data/price_history_checks_oct2019.xlsx", skiprows=2)   # load dataset

    df = normalize_data(df) # format data for necessary rows and columns

    fuel_list = ["E10", "U91", "P95", "P98"]  # list of supported fuel types

    for fuel in fuel_list:
        fuel_df = df.query('FuelCode == @fuel')
        test_model(fuel_df)
        #print(fuel_df)
        fuel_model = load_model(fuel_df)
        filename = "./models/fuel_model_" + fuel + ".sav"
        #print(filename)
    
        pickle.dump(fuel_model, open(filename, 'wb'))    # save model to memory

# loads a trained model for a given df
def load_model(df):
    model_x = df[['ServiceStationCode', 'PriceUpdatedDate']].values     # features that dictate prediction
    model_y = df['Price'].values                                        # feature to predict
   
    #print(model_x)
    #print(type(model_x))
    model = LinearRegression()
    model.fit(model_x, model_y)
    return model


# function to test accuracy of model with train and test data
def test_model(df):
    price_x_train, price_y_train, price_x_test, price_y_test = load_price(df, split_percentage=0.7)

    linear_model = LinearRegression()
    linear_model.fit(price_x_train, price_y_train)

    y_pred = linear_model.predict(price_x_test)
    
    print(y_pred)
    linearConfidence = linear_model.score(price_x_test, price_y_test)


if __name__ == "__main__":
    #init_model()

    #get_prediction(date, fuel_station_code, fuel_type)
    date = datetime.date(2019, 11, 21)  
    get_prediction(date, 0, "E10")  # test prediction