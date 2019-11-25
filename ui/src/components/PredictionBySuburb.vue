<template>
    <div class="row">
      <div class="col-md-12">
        <h2>Fuel Pricing by Location</h2>
        <label>Enter a NSW PostCode or Suburb</label>
        <br/><b-form-input v-model="location" placeholder="Suburb or PostCode"></b-form-input>
        <br/><b-form-input v-model="startDate" placeholder="Start date (form YYYY-MM-DD)"></b-form-input>
        <br/><b-form-input v-model="endDate" placeholder="End date (form YYYY-MM-DD)"></b-form-input>
        <br/><b-form-select text="Fuel Type" v-model="fuelType" :options="fuels"></b-form-select>
        <br/><br/><b-button variant="success" v-on:click="getPredictions">Find Me Baby!</b-button>
        <br/><br/>
        <Stations v-if="results" :result="results" :key="stationKey"/>
      </div>
    </div>
</template>

<script>
import axios from 'axios';
import Stations from './Stations';

export default {
  name: 'FuelPredictBySuburb',
  components: {
      Stations
  },
  data: function() {
    return {
      location: null,
      results: null,
      fuelType: null,
      startDate: null,
      endDate: null,
      fuels: [{ text: 'Fuel Type', value: null }, 'E10', 'U91', 'P98', 'P95'],
      stationKey: 0,
    }
  },
  methods: {
    getPredictions () {
        axios({
            method: 'GET',
            url: 'http://localhost:8003/token',
            headers: {
            'Accept': 'text/plain',
            'Content-Type': 'text/plain',
            'API_KEY': 'poontang'
            }
        }).then(response => {
            let token = response.data.tok
            axios({
                method: 'POST',
                url: 'http://localhost:8003/fuel/predictions/location',
                headers: {
                'Accept': 'text/plain',
                'Content-Type': 'text/plain',
                'AUTH_TOKEN': token
                },
                data: JSON.stringify({
                fuel_type: this.fuelType,
                prediction_start: this.startDate,
                prediction_end: this.endDate,
                named_location: this.location
            })
        }).then(response => {
          this.results = response.data[0]
          this.stationKey += 1
        }).catch(error => {
            console.log(error.response)
        })})       
    },
  }
}
</script>
