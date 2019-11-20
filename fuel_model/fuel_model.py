import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures, scale
from sklearn.pipeline import make_pipeline
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error'
from datetime import date
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
    
def init_model():
    df = pd.read_excel("fuel_data/service-station-price-history-june-2017.xlsx")
    #df = pd.read_excel("fuel_data_may-september_2017.xlsx")
    
    df_norm = normalize_data(df)

    price_x_train, price_y_train, price_x_test, price_y_test = load_price(df_norm, split_percentage=0.7)
    
    linear_model = LinearRegression()
    poly3_model = make_pipeline(PolynomialFeatures(3), Ridge())
    poly4_model = make_pipeline(PolynomialFeatures(4), Ridge())

    linear_model.fit(price_x_train, price_y_train)
    poly3_model.fit(price_x_train, price_y_train)
    poly4_model.fit(price_x_train, price_y_train)

    
    linearConfidence = linear_model.score(price_x_test, price_y_test)
    poly3Confidence = poly3_model.score(price_x_test, price_y_test)
    poly4Confidence = poly4_model.score(price_x_test, price_y_test)


    print("Linear confidence is: ", linearConfidence)
    print("Polynomial 3 confidence is: ", poly3Confidence)
    print("Polynomial 4 confidence is: ", poly4Confidence)
    
    # Try predict fuel price on 1/7/2019 as a test, not sure how PriceUpdatedDate has been formatted for this db
    price_x_predict = date.fromisoformat(2017, 7, 1)
    price_pred = poly3_model.predict(price_x_predict)
    
    df[price_x_predict.strftime("%d/%m/%y")] = price_pred
    
    return df

if __name__ == "__main__":
    init_model()
