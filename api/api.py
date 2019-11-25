from flask_restplus import Resource, Api
from flask import Flask, request
from flask_restplus import fields
import pandas as pd
import numpy as np

#from analytics import track_event

import logging
import requests
import sys
import os
sys.path.append(os.path.abspath('../fuel_model'))
import fuel_model as fm

import authentication

import json
import enum
from datetime import date
from numpy.core.arrayprint import DatetimeFormat
from datetime import timedelta, datetime
from flask.json import jsonify
from _ast import If
from pandas.tests.extension.test_external_block import df
from numpy.core.defchararray import lower

app = Flask(__name__)
api = Api(app,
          default="Fuel Prediction",
          title="Fuel Prediction API",
          description="API to return predicted fuel prices",
          authorizations= {
              'API_KEY': {
                  'type': 'apiKey',
                  'in': 'header',
                  'name': 'API_KEY'
              },
              'AUTH_TOKEN': {
                  'type': 'apiKey',
                  'in': 'header',
                  'name': 'AUTH_TOKEN'
              }
          })
auth = authentication.AuthToken()

@api.route('/token')
class Token(Resource):
    @api.doc(description="Gives an authentication token")
    @api.doc(security='API_KEY')
    def get(self):
        api_key = request.headers.get('API_KEY')
        # TODO check if valid api key e.g. in database
        if api_key:
            return {'tok': auth.generate()}
        else:
            return {'msg': 'API key invalid'}, 401

class FuelTypeEnum(enum.Enum):
    E10 = 'E10'
    U91 = 'U91'
    P98 = 'P98'
    P95 = 'P95'

fuel_list = ["E10", "U91", "P95", "P98"]

search_package = api.model('search', {
    'fuel_type' : fields.String(description='Fuel type for the fuel prediction'),# enum=['x.name for x in FuelTypeEnum']),
    'prediction_start' : fields.DateTime(description='start date for prediction period (yyyy-mm-dd)'),
    'prediction_end': fields.DateTime(description='end date for prediction period (yyyy-mm-dd)')
})

price_package = api.model('price', {
    'fuel_type' : fields.String(description='Fuel type for the fuel prediction'),# enum=['x.name for x in FuelTypeEnum']),
    'price_req' : fields.Integer(description='Desired Price for date prediction'),
    'prediction_start' : fields.DateTime(description='start date for prediction period (yyyy-mm-dd)'),
    'prediction_end': fields.DateTime(description='end date for prediction period (yyyy-mm-dd)')
})

location_model = api.model('location', {
    'fuel_type' : fields.String(description='Fuel type for the fuel prediction', enum=[x.name for x in FuelTypeEnum]),
    'named_location' : fields.String(description='suburb or postcode'),
    'prediction_start' : fields.DateTime(description='start date for prediction period (yyyy-mm-dd)'),
    'prediction_end': fields.DateTime(description='end date for prediction period (yyyy-mm-dd)')
})

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)

@api.route('/fuel/predictions/<int:station_code>')
@api.doc(params={'station_code': 'A petrol station station_code'})
class FuelPredictionsForStation(Resource):
    @api.doc(description="Returns fuel prediction prices for a single fuel type and petrol station",
            security='AUTH_TOKEN')
    @api.expect(search_package, validate=True)
    @api.response(200, "Successful")
    @api.response(400, "Fuel Type incorrect")
    @api.response(404, "Station not found")
    @api.response(401, "Authentication token missing or invalid")
    @authentication.authenticate(api, auth)
    def post(self, station_code):
        search = request.json

        if station_code not in df.ServiceStationCode:
            track_event(category='Fuel Prediction', action='Wrong Service Station')
            api.abort(404, "Station {} doesn't exist".format(station_code))

        fuel_type = search['fuel_type'].upper()
        if fuel_type not in fuel_list:
            track_event(category='Fuel Prediction', action='Wrong Fuel Type')
            api.abort(400, "Fuel Type {} is incorrect".format(fuel_type))

        start_date = date.fromisoformat(search['prediction_start'])
        end_date = date.fromisoformat(search['prediction_end'])

        prices = {}

        for single_date in daterange(start_date, end_date):
            prices[single_date.strftime("%Y-%m-%d")] = fm.get_prediction(single_date, station_code, fuel_type)

        ret = []
        print(station_code)
        df1 = df.query('ServiceStationCode == {}'.format(station_code))
        [name, address] = df1[['ServiceStationName', 'Address']].iloc[0]

        tmp = {
            'Status' : 'OK',
            'Station_Code' : station_code,
            'Station_Name' : name,
            'Station_Address' : address,
            'Fuel_Type' : fuel_type
            }

        for x in prices:
            tmp[x] = round(float(prices[x]), 2)

        ret.append(tmp)

        #track_event(category='Fuel Prediction', action='For Station')

        return ret


@api.route('/fuel/predictions/time/<int:station_code>')
class TimeForPriceAtStation(Resource):
    @api.doc(description="Returns earliest time for a predicted match to a given price at a station",
             security='AUTH_TOKEN')
    @api.expect(price_package, validate=True)
    @api.response(200, 'Successful')
    @api.response(400, "Fuel Type incorrect")
    @api.response(404, 'Station not found')
    @api.response(401, "Authentication token missing or invalid")
    @authentication.authenticate(api, auth)
    def post(self, station_code):
        search = request.json

        if station_code not in df.ServiceStationCode:
            track_event(category='Fuel Prediction', action='Wrong Service Station')
            api.abort(404, "Station {} doesn't exist".format(station_code))

        fuel_type = search['fuel_type'].upper()
        if fuel_type not in fuel_list:
            track_event(category='Fuel Prediction', action='Wrong Fuel Type')
            api.abort(400, "Fuel Type {} is incorrect".format(fuel_type))

        start_date = date.fromisoformat(search['prediction_start'])
        end_date = date.fromisoformat(search['prediction_end'])
        price_req = search['price_req']

        for single_date in daterange(start_date, end_date):
            if int(fm.get_prediction(single_date, station_code, fuel_type)) <= price_req:
                date_of_price = single_date.strftime("%Y-%m-%d")
                break
        else:
            return {"message": "Requested price ({}) was not found in requested time".format(price_req)}, 404

        ret = []

        df1 = df.query('ServiceStationCode == {}'.format(station_code))
        [name, address] = df1[['ServiceStationName', 'Address']].iloc[0]

        tmp = {
            'Status' : 'OK',
            'Station_Code' : station_code,
            'Station_Name' : name,
            'Station_Address' : address,
            'Fuel_Type' : fuel_type,
            'Price_Req' : price_req,
            'Date_of_Price' : date_of_price
            }

        ret.append(tmp)

        track_event(category='Fuel Prediction', action='Time For Prices')

        return ret


@api.route('/fuel/predictions/location')
class FuelPredictionsForLocation(Resource):
    @api.doc(description="Retuns fuel prediction prices for a single fuel type and a named location (suburb/postcode)",
            security='AUTH_TOKEN')
    @api.expect(location_model, validate=True)
    @api.response(200, 'Successful')
    @api.response(400, "Fuel Type incorrect")
    @api.response(404, 'Location not found')
    @api.response(401, "Authentication token missing or invalid")
    @authentication.authenticate(api, auth)
    def post(self):
        location = request.json

        req_loc = location['named_location']
        fuel_type = location['fuel_type'].upper()
        if fuel_type not in fuel_list:
            track_event(category='Fuel Prediction', action='Wrong Fuel Type')
            api.abort(400, "Fuel Type {} is incorrect".format(fuel_type))

        if req_loc in df.Suburb.unique():
            track_event(category='Fuel Prediction', action='Suburb Entered')
            print('its a suburb!')
            df1 = df.loc[df['Suburb'] == req_loc]
        elif req_loc not in df.Postcode.unique():
            track_event(category='Fuel Prediction', action='Postcode Entered')
            print('its a postcode!')
            df1 = df.query('Postcode == {}'.format(req_loc))
        else:
            track_event(category='Fuel Prediction', action='Invalid Location')
            return {"message": "Location {} not found".format(req_loc)}, 404

        stations = df1.ServiceStationCode.unique()

        start_date = date.fromisoformat(location['prediction_start'])
        end_date = date.fromisoformat(location['prediction_end'])

        prices= {}

        for single_date in daterange(start_date, end_date):
            date_string = single_date.strftime("%Y-%m-%d")
            prices[date_string] = []
            for i in stations:
                prices[date_string].append(int(fm.get_prediction(single_date, i, fuel_type)))

        ret = []

        tmp = {
            'Status' : 'OK',
            'Requested_Loc' : req_loc,
            'Fuel_Type' : fuel_type,
            }

        for x in prices:
            tmp[x] = np.mean(prices[x])

        ret.append(tmp)

        track_event(category='Fuel Prediction', action='For Location')

        return ret


@api.route('/fuel/predictions/average')
class AverageFuelPredictionForSuburb(Resource):
    @api.doc(description="Returns average predicted fuel price for a given suburb",
             security='AUTH_TOKEN')
    @api.expect(location_model, validate=True)
    @api.response(200, 'Successful')
    @api.response(400, "Fuel Type incorrect")
    @api.response(404, 'Location not found')
    @api.response(401, "Authentication token missing or invalid")
    @authentication.authenticate(api, auth)
    def post(self):
        location = request.json

        req_loc = location['named_location']
        fuel_type = location['fuel_type'].upper()
        if fuel_type not in fuel_list:
            track_event(category='Fuel Prediction', action='Wrong Fuel Type')
            api.abort(400, "Fuel Type {} is incorrect".format(fuel_type))

        if req_loc in df.Suburb.unique():
            track_event(category='Fuel Prediction', action='Location Entered')
            print('its a suburb!')
            df1 = df.loc[df['Suburb'] == req_loc]
        elif req_loc not in df.Postcode.unique():
            track_event(category='Fuel Prediction', action='Postcode Entered')
            print('its a postcode!')
            df1 = df.query('Postcode == {}'.format(req_loc))
        else:
            track_event(category='Fuel Prediction', action='Invalid Location')
            return {"message": "Location {} not found".format(req_loc)}, 404

        stations = df1.ServiceStationCode.unique()

        start_date = date.fromisoformat(location['prediction_start'])
        end_date = date.fromisoformat(location['prediction_end'])

        prices= []

        for single_date in daterange(start_date, end_date):
            for i in stations:
                prices.append(int(fm.get_prediction(single_date, i, fuel_type)))


        ret = []

        tmp = {
            'Status' : 'OK',
            'Requested_Loc' : req_loc,
            'Fuel_Type' : fuel_type,
            'Ave_Price' : np.mean(prices)
            }

        ret.append(tmp)

        track_event(category='Fuel Prediction', action='Average Fuel For Suburbs')

        return ret




if __name__ == "__main__":
    #df = fm.api_read()
    df = pd.read_excel("fuel_data/price_history_checks_oct2019.xlsx", skiprows=2)
    
    print(df)
    df = df.dropna()


    df2 = df.query('1000 <= Postcode <= 2249')
    df3 = df.query('2760 <= Postcode <= 2770')
 
    df = df2.append(df3, ignore_index=True)
    df['PriceUpdatedDate'] = df['PriceUpdatedDate'].apply(fm.extract_date)
    
    map_df = pd.read_csv("station_code_mapping.csv")   
    df = pd.merge(map_df, df, how='inner', on='ServiceStationName')    
    print(df)

    #print(df1.head(5).to_string())

    app.run(debug=True, port=8003)
