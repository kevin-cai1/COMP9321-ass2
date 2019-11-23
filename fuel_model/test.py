import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures, scale
from sklearn.pipeline import make_pipeline
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error, r2_score
from sklearn import model_selection
import pickle
import numpy as np
import datetime


def load_price(df, split_percentage):
    df = shuffle(df)

    price_x = df[['PriceUpdatedDate']].values
    price_y = df['Price'].values

    price_x = scale(price_x)

    split_point = int(len(price_x) * split_percentage)
    price_x_train = price_x[:split_point]
    price_y_train = price_y[:split_point]
    price_x_test = price_x[split_point:]
    price_y_test = price_y[split_point:]

    return price_x_train, price_y_train, price_x_test, price_y_test

    

def normalize_data(df):
    df['PriceUpdatedDate'] = df['PriceUpdatedDate'].apply(extract_date)   # format date to be ordinal date

    df = df.query('FuelCode == "E10"')
    df = df.query('ServiceStationName =="Metro Fuel Marrickville"')

    df1 = df[['PriceUpdatedDate', 'Price']]
    print(df1)
    df1 = df1.sort_values(by=['PriceUpdatedDate'])    
    return df1

def extract_date(x):
    x = str(x).split(' ')   # gets just the date
    x = x[0]
    date = x.split('/')
    date_date = datetime.date(int(date[2]), int(date[1]), int(date[0])) #date(year, month, day)
    return date_date.toordinal()
    
if __name__ == "__main__":
    #df = pd.read_excel("fuel_data/service-station-price-history-june-2017.xlsx")
    df = pd.read_excel('fuel_data/price_history_checks_oct2019.xlsx', skiprows=2)
    df = df.dropna()
    print(df)
    #df = pd.read_excel("fuel_data_may-september_2017.xlsx")
    #df = pd.read_excel("marrickville_4_months.xlsx")
    #df = pd.read_excel("marrickville.xlsx")
    df = normalize_data(df)
    #df = df[['PriceUpdatedDate', 'Price']]

    price_x_train, price_y_train, price_x_test, price_y_test = load_price(df, split_percentage=0.7)
    
    linear_model = LinearRegression()
    knn_model = KNeighborsRegressor(n_neighbors=2)
    poly3_model = make_pipeline(PolynomialFeatures(3), Ridge())
    poly4_model = make_pipeline(PolynomialFeatures(4), Ridge())
    gbr_model = GradientBoostingRegressor(loss='ls', max_depth=6)
    decision_tree_model = DecisionTreeRegressor(random_state=0)

    linear_model.fit(price_x_train, price_y_train)
    #knn_model.fit(price_x_train, price_y_train)
    poly3_model.fit(price_x_train, price_y_train)
    poly4_model.fit(price_x_train, price_y_train)
    gbr_model.fit(price_x_train, price_y_train)
    decision_tree_model.fit(price_x_train, price_y_train)


    #filename = 'model.sav'
    #pickle.dump(linear_model, open(filename, 'wb'))

    y_pred = linear_model.predict(price_x_test)
    y_pred1 = poly3_model.predict(price_x_test)
    y_pred2 = poly4_model.predict(price_x_test)
    y_pred3 = gbr_model.predict(price_x_test)
    y_pred4 = decision_tree_model.predict(price_x_test)

    #print(price_x_test)
    #print(type(price_x_test))
    #print(type(price_y_test))
    #print(price_y_test)

    #y_pred2 = knn_model.predict(price_x_test)

    #for i in range(len(price_y_test)):
    #    print("Linear Expected: ", price_y_test[i], "Linear Predicted:", y_pred[i])

    #for i in range(len(price_y_test)):
    #    print("KNN Expected: ", price_y_test[i], "KNN Predicted:", y_pred2[i])
    
    linearConfidence = linear_model.score(price_x_test, price_y_test)
    #knnConfidence = knn_model.score(price_x_test, price_y_test)
    poly3Confidence = poly3_model.score(price_x_test, price_y_test)
    poly4Confidence = poly4_model.score(price_x_test, price_y_test)
    gbrConfidence = gbr_model.score(price_x_test, price_y_test)
    dtrConfidence = decision_tree_model.score(price_x_test, price_y_test)


    print("Linear confidence is: ", linearConfidence)
    #print("KNN confidence is: ", knnConfidence)
    print("Polynomial 3 confidence is: ", poly3Confidence)
    print("Polynomial 4 confidence is: ", poly4Confidence)
    print("Gradient Boosting confidence is: ", gbrConfidence)
    print("Decision Tree confidence is: ", dtrConfidence)
    print("")
    print("Linear mean squared error: %.2f" % mean_squared_error(price_y_test, y_pred))
    print("Polynomial 3 mean squared error: %.2f" % mean_squared_error(price_y_test, y_pred1))
    print("Polynomial 4 mean squared error: %.2f" % mean_squared_error(price_y_test, y_pred2))
    print("Gradient Boosting Regressor mean squared error: %.2f" % mean_squared_error(price_y_test, y_pred3))
    print("Decision Tree Regressor mean squared error: %.2f" % mean_squared_error(price_y_test, y_pred4))
    print("")
    print("Linear R^2 score: ", r2_score(price_y_test, y_pred))
    print("Polynomial 3 R^2 score: ", r2_score(price_y_test, y_pred1))
    print("Polynomial 4 R^2 score: ", r2_score(price_y_test, y_pred2))
    print("Gradient Boosting Regressor R^2 score: ", r2_score(price_y_test, y_pred3))
    print("Decision Tree Regressor R^2 score: ", r2_score(price_y_test, y_pred4))

    #print("KNN Mean squared error: %.2f" % mean_squared_error(price_y_test, y_pred2))
