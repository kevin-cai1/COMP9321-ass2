import pandas as pd
from sklearn import linear_model, preprocessing, neighbors
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error
import numpy as np


def load_price(df, split_percentage):
    df = shuffle(df)

    price_x = df.drop('Price', axis=1).values
    price_y = df['Price'].values

    price_x = preprocessing.scale(price_x)

    split_point = int(len(price_x) * split_percentage)
    price_x_train = price_x[:split_point]
    price_y_train = price_y[:split_point]
    price_x_test = price_x[split_point:]
    price_y_test = price_y[split_point:]

    return price_x_train, price_y_train, price_x_test, price_y_test

    

def normalize_data(df):
    #df = df.query('FuelCode == "E10"')
    #df = df.query('ServiceStationName =="7-Eleven Artarmon"')

    df1 = df[['PriceUpdatedDate', 'Price']]

    df1 = df1.sort_values(by=['PriceUpdatedDate'])    
    return df1
    
if __name__ == "__main__":
    #df = pd.read_csv("fuel_data_june_2017_normalised.csv")
    #df = pd.read_excel("service-station-price-history-june-2017.xlsx")
    #df = pd.read_csv("fuel_data_may-september_2017_normalised.csv")
    df = pd.read_excel("fuel_data_may-september_2017.xlsx")
    print(df)
    df = normalize_data(df)

    price_x_train, price_y_train, price_x_test, price_y_test = load_price(df, split_percentage=0.7)
    
    model = linear_model.LinearRegression()

    model2 = neighbors.KNeighborsRegressor(n_neighbors=2)
    

    model.fit(price_x_train, price_y_train)
    model2.fit(price_x_train, price_y_train)

    y_pred = model.predict(price_x_test)

    y_pred2 = model2.predict(price_x_test)

    for i in range(len(price_y_test)):
        print("Linear Expected: ", price_y_test[i], "Linear Predicted:", y_pred[i])

    for i in range(len(price_y_test)):
        print("KNN Expected: ", price_y_test[i], "KNN Predicted:", y_pred2[i])
    

    print("Mean squared error: %.2f" % mean_squared_error(price_y_test, y_pred))
    print("Mean squared error: %.2f" % mean_squared_error(price_y_test, y_pred2))
