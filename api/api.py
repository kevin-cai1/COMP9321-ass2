from flask_restplus import Resource, Api
from flask import Flask, request
from flask_restplus import fields

from . import fuel_model

import json
import enum

app = Flask(__name__)
api = Api(app, default="Fuel Prediction", title="Fuel Prediction API", description="API to return predicted fuel prices")

class FuelTypeEnum(enum.Enum):
    E10 = 'E10'
    U91 = 'U91'
    DL = 'DL'
    P98 = 'P98'
    P95 = 'P95'

search_package = api.model('search', {
    'fuel_type' : fields.String(description='Fuel type for the fuel prediction', enum=['x.name for x in FuelTypeEnum']),
    'prediction_start' : fields.DateTime(description='start date for prediction period'),
    'prediction_end': fields.DateTime(description='end date for prediction period')
})

location_model = api.model('location', {
    'fuel_type' : fields.String(description='Fuel type for the fuel prediction', enum=[x.name for x in FuelTypeEnum]),
    'named_location' : fields.String(description='suburb or postcode'),
    'prediction_start' : fields.DateTime(description='start date for prediction period'),
    'prediction_end': fields.DateTime(description='end date for prediction period')
})

prediction_model = api.model('prediction', {
    'station_name' : fields.String(description='Name of fuel station'),
    'named_location' : fields.String(description='suburb or postcode'),
    'fuel_type' : fields.String(description='Fuel type for the fuel prediction', enum=[x.name for x in FuelTypeEnum]),
    'date' : fields.DateTime(description='date for price predicted')
})

@api.route('/fuel/predictions/<int:station_code>')
@api.doc(params={'station_code': 'A petrol station station_code'})
class FuelPredictionsForStation(Resource):
    @api.doc(description="Returns fuel prediction prices for a single fuel type and petrol station")
    @api.expect(search_package, validate=True)
    @api.response(200, "Successful")
    @api.response(404, "Station was not found")
    def post(self):
        search = request.json
        
        if 'station_code' not in search or search['station_code'] not in df.index:
            api.abort(404, "Station {} doesn't exist.".format(search['station_code']))
            
        prediction = dict('station_name': df.at[station_code, 'ServiceStationName'],
                          'suburb': df.at[station_code, 'Suburb'],
                          'postcode': df.at[station_code, 'Postcode'],
                          'fuel_type': df.at[station_code, 'FuelCode'],
                          'price': df.at[station_code, '01/07/2017'] #just return test date for now
                         )
        return prediction
                          


@api.route('/fuel/predictions/time/<int:station_code>')
class TimeForPriceAtStation(Resource):
    @api.doc(description="Returns earliest time for a predicted match to a given price at a station")
    @api.expect(search_package, validate=True)
    @api.response(200, "Successful")
    @api.response(404, "Station/Prediction was not found")
    def post(self):
        search = request.json
        
        if 'station_code' not in search or search['station_code'] not in df.index:
            api.abort(404, "Station {} doesn't exist.".format(search['station_code']))
            
        if 'prediction_start' not in search or search['prediction_start'] not in df.columns:
            api.abort(404, "Prediction date {} not valid.".format(search['prediction_start']))
        pass


@api.route('/fuel/predictions/location')
class FuelPredictionsForLocation(Resource):
    @api.doc(description="Returns fuel prediction prices for a single fuel type and a named location (suburb/postcode)")
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
    df = fuel_model.init_model()    # possibly make a df for each suburb?
    app.run(debug=True, port=8002)
