from flask import Flask, request, render_template
from flask_wtf import FlaskForm, Form, widgets
from wtforms import StringField, SelectField, SelectMultipleField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, Length, Required
from wtforms.widgets import TableWidget, ListWidget, CheckboxInput

class MultiCheckboxField(SelectMultipleField):
	widget			= TableWidget()
	option_widget	= CheckboxInput()

class ServicesForm(Form):
    list_of_services = ["7-Eleven", "BP", "Budget", "Caltex", "Caltex Woolworths", "Coles", "Enhance", "Independant", "Inland", "Liberty", "Lowes", "Matilda", "Metro", "Mobil", "NRMA", "Prime", "Puma", "Shell", "Southwest", "Speedway", "United"]
    # create a list of value/description tuples
    files = [(x, x) for x in list_of_services]
    services = MultiCheckboxField('Label', choices=files)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

class FuelForm(FlaskForm):
    fuel_type = SelectField(u'fuel_type', choices=[('E10','Ethanol 94 (E10)'), ('P98', 'Premium 98'), ('P95', 'Premium 95'), ('U91', 'Unleaded 91'), ('DL', 'Diesel') ])
    postcode = StringField(u'postcode', validators=[InputRequired('Postcode required'), Length(min=4, max=4, message="Postcode must be 4 digits")])
    prediction_date = DateField(u'prediction_date', format='%Y-%m-%d', validators=[InputRequired('Prediction date required')])
    list_of_services = ["7-Eleven", "BP", "Budget", "Caltex", "Caltex Woolworths", "Coles", "Enhance", "Independant", "Inland", "Liberty", "Lowes", "Matilda", "Metro", "Mobil", "NRMA", "Prime", "Puma", "Shell", "Southwest", "Speedway", "United"]
    # create a list of value/description tuples
    files = [(x, x) for x in list_of_services]
    services = MultiCheckboxField(u'services', choices=files)

@app.route('/', methods=['POST', 'GET'] )
def home():
    form = FuelForm()

    if form.validate_on_submit():
        return "Form has been submitted with fuel type: {}, postcode: {}, prediction_date: {}, services: {}".format(form.fuel_type.data, form.postcode.data, form.prediction_date.data, form.services.data)

    return render_template("home.html", form=form)

@app.route('/about', methods=['GET'])
def about():

    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
