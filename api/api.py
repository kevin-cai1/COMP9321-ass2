from flask_restplus import Resource, Api
from flask import Flask, request
from flask_restplus import fields
import pandas as pd
import numpy as np

import fuel_model as fm
    
import json
import enum
from datetime import date
from numpy.core.arrayprint import DatetimeFormat
from Lib.datetime import timedelta, datetime
from flask.json import jsonify

app = Flask(__name__)
api = Api(app, default="Fuel Prediction", title="Fuel Prediction API", description="API to return predicted fuel prices")

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

location_model = api.model('location', {
    'fuel_type' : fields.String(description='Fuel type for the fuel prediction', enum=[x.name for x in FuelTypeEnum]),
    'named_location' : fields.String(description='suburb or postcode'),
    'prediction_start' : fields.DateTime(description='start date for prediction period (yyyy-mm-dd)'),
    'prediction_end': fields.DateTime(description='end date for prediction period (yyyy-mm-dd)')
})

prediction_model = api.model('prediction', {
    'station_name' : fields.String(description='Name of fuel station'),
    'fuel_type' : fields.String(description='Fuel type for the fuel prediction', enum=[x.name for x in FuelTypeEnum]),
    'date' : fields.DateTime(description='date for price predicted (yyyy-mm-dd)')
})

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)

@api.route('/fuel/predictions/<int:station_code>')
@api.doc(params={'station_code': 'A petrol station station_code'})
class FuelPredictionsForStation(Resource):
    @api.doc(description="Returns fuel prediction prices for a single fuel type and petrol station")
    @api.expect(search_package, validate=True)
    @api.response(200, "Successful")
    @api.response(404, "Station/Fuel_Type not found")
    def post(self, station_code):
        search = request.json
        
        if station_code not in df.ServiceStationCode:
            api.abort(404, "Station {} doesn't exist".format(station_code))
          
        fuel_type = search['fuel_type'].upper()
        if fuel_type not in fuel_list:
            api.abort(404, "Fuel Type {} doesn't exist".format(fuel_type))
            
        start_date = date.fromisoformat(search['prediction_start'])
        end_date = date.fromisoformat(search['prediction_end'])
        
        prices = {}
        
        for single_date in daterange(start_date, end_date):
            print(single_date.strftime("%Y-%m-%d"))
            prices[single_date.strftime("%Y-%m-%d")] = fm.get_prediction(single_date, station_code, fuel_type)
        
        ret = []
                  
        tmp = {
            'Status' : 'OK',
            'Station_Code' : station_code,
            'Station_Address' : 'address',
            'Fuel_Type' : fuel_type
            }
        
        for x in prices:
            tmp[x] = int(prices[x])

        ret.append(tmp)
        
        return ret


@api.route('/fuel/predictions/time/<int:station_code>')
class TimeForPriceAtStation(Resource):
    @api.doc(description="Returns earliest time for a predicted match to a given price at a station")
    @api.expect(search_package, validate=True)
    def post(self):
        pass


@api.route('/fuel/predictions/location')
class FuelPredictionsForLocation(Resource):
    @api.doc(description="Retuns fuel prediction prices for a single fuel type and a named location (suburb/postcode)")
    @api.expect(location_model, validate=True)
    def post(self):
        pass


@api.route('/fuel/predictions/average')
class AverageFuelPredictionForSuburb(Resource):
    @api.doc(description="Returns average predicted fuel price for a given suburb")
    @api.expect(location_model, validate=True)
    def post(self):
        pass


if __name__ == "__main__":

    df = pd.read_excel("fuel_data/price_history_checks_oct2019.xlsx", skiprows=2)
    
    
    df2 = df.query('1000 <= Postcode <= 2249')
    df3 = df.query('2760 <= Postcode <= 2770')
 
    df = df2.append(df3, ignore_index=True)
    df = df.dropna()
    df['PriceUpdatedDate'] = df['PriceUpdatedDate'].apply(fm.extract_date)
    
    map_df = pd.read_csv("station_code_mapping.csv")   
    df = pd.merge(map_df, df, how='inner', on='ServiceStationName')

    # print(df.head(5).to_string())

    app.run(debug=True, port=8002)
    
    