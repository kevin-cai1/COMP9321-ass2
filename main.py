# [START gae_flex_analytics_track_event]
import logging
import os
import requests

from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, Length

app = Flask(__name__)

# Environment variables are defined in app.yaml.
GA_TRACKING_ID = os.environ['GA_TRACKING_ID']

app.config['SECRET_KEY'] = 'secret_key'

# Event tracker
def track_event(category, action, label=None, value=0):
    data = {
        'v': '1',  # API Version.
        'tid': GA_TRACKING_ID,  # Tracking ID / Property ID.
        # Anonymous Client Identifier. Ideally, this should be a UUID that
        # is associated with particular user, device, or browser instance.
        'cid': randint(),
        't': 'event',  # Event hit type.
        'ec': category,  # Event category.
        'ea': action,  # Event action.
        'el': label,  # Event label.
        'ev': value,  # Event value, must be an integer
    }

    response = requests.post('https://www.google-analytics.com/collect', data=data)

    # If the request fails, this will raise a RequestException. Depending
    # on your application's needs, this may be a non-error and can be caught
    # by the caller.
    response.raise_for_status()

class FuelForm(FlaskForm):
    fuel_type = SelectField(u'fuel_type', choices=[('E10','Ethanol 94 (E10)'), ('P98', 'Premium 98'), ('P95', 'Premium 95'), ('U91', 'Unleaded 91'), ('DL', 'Diesel') ])
    postcode = StringField(u'postcode', validators=[InputRequired('Postcode required'), Length(min=4, max=4, message="Postcode must be 4 digits")])
    prediction_date = DateField(u'prediction_date', format='%Y-%m-%d', validators=[InputRequired('Prediction date required')])

@app.route('/', methods=['POST', 'GET'] )
def home():
    form = FuelForm()

    track_event(category='Home', action='View')

    if form.validate_on_submit():
        track_event(category='Predict', action='Submit')
        return "Form has been submitted with fuel type: {}, postcode: {}, prediction_date: {}".format(form.fuel_type.data, form.postcode.data, form.prediction_date.data)

    return render_template("home.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)
