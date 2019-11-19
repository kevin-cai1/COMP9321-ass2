from flask_restplus import Resource, Api

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

@api.route('/fuel/predictions/<int:station_code>')
@api.doc(params={'station_code': 'A petrol station station_code'})
class FuelPredictionsForStation(Resource):
    @api.doc(description="Returns fuel prediction prices for a single fuel type and petrol station")
    @api.expect(search_package, validate=True)
    def post(self):
        pass


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
    app.run(debug=True, port=8002)