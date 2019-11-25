from flask_restplus import Resource, Api
from flask import Flask, request
from flask_restplus import fields
import pandas as pd
import numpy as np
from backports.datetime_fromisoformat import MonkeyPatch
MonkeyPatch.patch_fromisoformat()

#from analytics import #track_event

import logging
import requests
import sys
import os
sys.path.append(os.path.abspath('../fuel_model'))
import fuel_model as fm

import authentication

import json
import enum
import re
from datetime import date
from numpy.core.arrayprint import DatetimeFormat
from datetime import timedelta, datetime
from flask.json import jsonify
from _ast import If
from pandas.tests.extension.test_external_block import df
from numpy.core.defchararray import lower
from flask_cors import CORS

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
CORS(app)


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
    # @api.expect(search_package, validate=True)
    @api.response(200, "Successful")
    @api.response(400, "Fuel Type incorrect")
    @api.response(400, "Date Type incorrect")
    @api.response(404, "Station not found")
    @api.response(401, "Authentication token missing or invalid")
    @authentication.authenticate(api, auth)
    def post(self, station_code):
        req = request.get_json(force=True)

        if station_code not in df.ServiceStationCode:
            #track_event(category='Fuel Prediction', action='Wrong Service Station')
            api.abort(404, "Station {} doesn't exist".format(station_code))

        fuel_type = req['fuel_type'].upper()
        if fuel_type not in fuel_list:
            #track_event(category='Fuel Prediction', action='Wrong Fuel Type')
            api.abort(400, "Fuel Type {} is incorrect".format(fuel_type))

        start_date = _parse_date(req['prediction_start'])
        end_date = _parse_date(req['prediction_end'])
        prices = {}

        for single_date in daterange(start_date, end_date):
            prices[single_date.strftime("%Y-%m-%d")] = fm.get_prediction(single_date, station_code, fuel_type)

        ret = []

        df1 = df.query('ServiceStationCode == {}'.format(station_code))
        if not df1.empty:
            [name, address] = df1[['ServiceStationName', 'Address']].iloc[0]

            tmp = {
                'Status' : 'OK',
                'Station_Code' : station_code,
                'Station_Name' : name,
                'Station_Address' : address,
                'Fuel_Type' : fuel_type,
                'Prices': list()
                }

        for x in prices:
            price = {
                'date': x,
                'price': round(float(prices[x]), 2)
            }
            tmp['Prices'].append(price)


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
        req = request.get_json(force=True)

        if station_code not in df.ServiceStationCode:
            #track_event(category='Fuel Prediction', action='Wrong Service Station')
            api.abort(404, "Station {} doesn't exist".format(station_code))

        fuel_type = req['fuel_type'].upper()
        if fuel_type not in fuel_list:
            #track_event(category='Fuel Prediction', action='Wrong Fuel Type')
            api.abort(400, "Fuel Type {} is incorrect".format(fuel_type))

        start_date = _parse_date(req['prediction_start'])
        end_date = _parse_date(req['prediction_end'])
        price_req = req['price_req']

        for single_date in daterange(start_date, end_date):
            if int(fm.get_prediction(single_date, station_code, fuel_type)) <= price_req:
                date_of_price = single_date.strftime("%Y-%m-%d")
                break
        else:
            return {"message": "Requested price ({}) was not found in requested time".format(price_req)}, 404

        ret = []

        df1 = df.query('ServiceStationCode == {}'.format(station_code))
        if not df1.empty:
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

        #track_event(category='Fuel Prediction', action='Time For Prices')

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
        req = request.json

        fuel_type = req['fuel_type'].upper()
        if fuel_type not in fuel_list:
            #track_event(category='Fuel Prediction', action='Wrong Fuel Type')
            api.abort(400, "Fuel Type {} is incorrect".format(fuel_type))

        req_loc = req['named_location'].lower()
        loc_df = _location_query(req_loc, df)
        if loc_df.empty:
           return {"message": "Location {} not found".format(req_loc)}, 404
           #track_event(category='Fuel Prediction', action='Invalid Location')

        start_date = _parse_date(req['prediction_start'])
        end_date = _parse_date(req['prediction_end'])
        prices= {}
        stations = loc_df.ServiceStationCode.unique()

        for single_date in daterange(start_date, end_date):
            date_string = single_date.strftime("%Y-%m-%d")
            prices[date_string] = []
            for i in stations:
                prices[date_string].append(int(fm.get_prediction(single_date, i, fuel_type)))

        prices = {}
        for station in stations:
            station_prices = []
            for single_date in daterange(start_date, end_date):
                date_string = single_date.strftime("%Y-%m-%d")
                station_prices.append(round(float(fm.get_prediction(single_date, station, fuel_type)), 2))
            print(station_prices)
            print(station)
            prices[station] = station_prices

        print(prices)
        ret = []

        for station in prices:
            price = (round(float(np.mean(prices[station])), 2))
            print(station)
            tmp = {
            'Status' : 'OK',
            'Requested_Loc' : req_loc,
            'Station_Code' : int(station),
            'Fuel_Type' : fuel_type,
            'AveragePrice' : price
            }
            ret.append(tmp)

        #track_event(category='Fuel Prediction', action='For Location')

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
        req = request.json

        fuel_type = req['fuel_type'].upper()
        if fuel_type not in fuel_list:
            #track_event(category='Fuel Prediction', action='Wrong Fuel Type')
            api.abort(400, "Fuel Type {} is incorrect".format(fuel_type))

        req_loc = req['named_location'].lower()
        loc_df = _location_query(req_loc, df)
        if loc_df.empty:
            #track_event(category='Fuel Prediction', action='Invalid Location')
            return {"message": "Location {} not found".format(req_loc)}, 404

        stations = loc_df.ServiceStationCode.unique()
        start_date = _parse_date(req['prediction_start'])
        end_date = _parse_date(req['prediction_end'])
        prices= []

        for single_date in daterange(start_date, end_date):
            for i in stations:
                prices.append(int(fm.get_prediction(single_date, i, fuel_type)))

        ret = [{
            'Status' : 'OK',
            'Requested_Loc' : req_loc,
            'Fuel_Type' : fuel_type,
            'Ave_Price' : np.mean(prices)
            }]
        #track_event(category='Fuel Prediction', action='Average Fuel For Suburbs')

        return ret

def _parse_date(d: str) -> date:
    try:
        return date.fromisoformat(d)
    except ValueError:
        api.abort(400, "Date {} is wrong format, expected YYYY-MM-DD".format(d))

# Returns subset of dataframe matching loc
# Returns empty dataframe if none match
def _location_query(loc: str, df: pd.DataFrame) -> pd.DataFrame:
    # Postcode
    if re.fullmatch(r'^[0-9]{4}$', loc):
        #track_event(category='Fuel Prediction', action='Postcode Entered')
        result = df.query('Postcode == @loc')
    # Surburb
    elif re.fullmatch(r'^\w+$', loc):
        result = df.query('Suburb == @loc')
        #track_event(category='Fuel Prediction', action='Suburb Entered')
    else:
        result = pd.DataFrame()

    return result

if __name__ == "__main__":
    #df = fm.api_read()
    df = pd.read_excel("fuel_data/price_history_checks_oct2019.xlsx", skiprows=2)

    print(df)
    df = df.dropna()


    df2 = df.query('1000 <= Postcode <= 2249')
    df3 = df.query('2760 <= Postcode <= 2770')

    df = df2.append(df3, ignore_index=True)
    df = df.dropna()
    df['PriceUpdatedDate'] = df['PriceUpdatedDate'].apply(fm.extract_date)

    map_df = pd.read_csv("station_code_mapping.csv")
    df = df.merge(map_df, how='inner', on='ServiceStationName')
    df['Suburb'] = df['Suburb'].str.lower()
    print(df)

    #print(df1.head(5).to_string())

    app.run(debug=True, port=8003)
