import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor

from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures, scale
from sklearn.pipeline import make_pipeline
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error
from sklearn import model_selection
import pickle
import numpy as np


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
    df = df.query('FuelCode == "E10"')
    df = df.query('ServiceStationName =="7-Eleven Artarmon"')

    df1 = df[['PriceUpdatedDate', 'Price']]

    df1 = df1.sort_values(by=['PriceUpdatedDate'])    
    return df1
    
if __name__ == "__main__":
    df = pd.read_excel("fuel_data/service-station-price-history-june-2017.xlsx")
    #df = pd.read_excel("fuel_data_may-september_2017.xlsx")
    print(df)
    df = normalize_data(df)

    price_x_train, price_y_train, price_x_test, price_y_test = load_price(df, split_percentage=0.7)
    
    linear_model = LinearRegression()
    knn_model = KNeighborsRegressor(n_neighbors=2)
    poly3_model = make_pipeline(PolynomialFeatures(3), Ridge())
    poly4_model = make_pipeline(PolynomialFeatures(4), Ridge())

    linear_model.fit(price_x_train, price_y_train)
    #knn_model.fit(price_x_train, price_y_train)
    poly3_model.fit(price_x_train, price_y_train)
    poly4_model.fit(price_x_train, price_y_train)

    filename = 'model.sav'
    pickle.dump(linear_model, open(filename, 'wb'))

    y_pred = linear_model.predict(price_x_test)

    #y_pred2 = knn_model.predict(price_x_test)

    #for i in range(len(price_y_test)):
    #    print("Linear Expected: ", price_y_test[i], "Linear Predicted:", y_pred[i])

    #for i in range(len(price_y_test)):
    #    print("KNN Expected: ", price_y_test[i], "KNN Predicted:", y_pred2[i])
    
    linearConfidence = linear_model.score(price_x_test, price_y_test)
    #knnConfidence = knn_model.score(price_x_test, price_y_test)
    poly3Confidence = poly3_model.score(price_x_test, price_y_test)
    poly4Confidence = poly4_model.score(price_x_test, price_y_test)


    print("Linear confidence is: ", linearConfidence)
    #print("KNN confidence is: ", knnConfidence)
    print("Polynomial 3 confidence is: ", poly3Confidence)
    print("Polynomial 4 confidence is: ", poly4Confidence)

    print("Linear Mean squared error: %.2f" % mean_squared_error(price_y_test, y_pred))
    #print("KNN Mean squared error: %.2f" % mean_squared_error(price_y_test, y_pred2))
