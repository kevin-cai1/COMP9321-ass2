<template>
    <div class="row">
      <div class="col-md-12">
        <h2>Fuel Pricing by Station</h2>
        <label>Start typing the name of a fuel station and the field will auto-complete</label>
        <v-autocomplete :items="items" v-model="item" :get-label="setLabel" :component-item="itemTemplate" @update-items="inputChange" @item-selected="itemSelected"></v-autocomplete>
        <br/><b-form-input v-model="startDate" placeholder="Start date (form YYYY-MM-DD)"></b-form-input>
        <br/><b-form-input v-model="endDate" placeholder="End date (form YYYY-MM-DD)"></b-form-input>
        <br/><b-form-select text="Fuel Type" v-model="fuelType" :options="fuels"></b-form-select>
        <br/><br/><b-button variant="success" v-on:click="getPredictions">Predict Me Baby!</b-button>
        <br/><br/>
        <Station v-if="results" :result="results" :key="stationKey"/>
      </div>
    </div>
</template>

<script>
import itemTemplate from './ItemTemplate.vue';
import Autocomplete from 'v-autocomplete';
import Station from './Station.vue'
import axios from 'axios';

export default {
  name: 'FuelPredictByStation',
  data: function() {
    return {
      item: null,
      itemTemplate,
      items: this.hardcodedStationList,
      results: null,
      startDate: null,
      endDate: null,
      fuelType: null,
      fuels: [{ text: 'Fuel Type', value: null }, 'E10', 'U91', 'P98', 'P95'],
      stationKey: 0,
    }
  },
  components: {
    'v-autocomplete': Autocomplete,
    'Station': Station
  },
  props: {
    hardcodedStationList: Array
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
                url: 'http://localhost:8003/fuel/predictions/'+this.item.id,
                headers: {
                'Accept': 'text/plain',
                'Content-Type': 'text/plain',
                'AUTH_TOKEN': token
                },
                data: JSON.stringify({
                fuel_type: this.fuelType,
                prediction_start: this.startDate,
                prediction_end: this.endDate
            })
        }).then(response => {
          this.results = response.data[0]
          this.stationKey += 1
        })})       
    },
    itemSelected (item) {
      this.item = item
    },
    setLabel (item) {
      if (item != null) {
        return item.name
      }
      return null
    },
    inputChange (text) {
      this.items = this.hardcodedStationList.filter(item => item.name.toLowerCase().includes(text.toLowerCase()))
    },
  }
}
</script>

<style lang="stylus">
.v-autocomplete
  .v-autocomplete-input-group
    .v-autocomplete-input
      padding 10px 15px
      box-shadow none
      border 1px solid #428bca
      width calc(100%)
      outline none
      background-color #eee
    &.v-autocomplete-selected
      .v-autocomplete-input
        color green
        background-color #f2fff2
  .v-autocomplete-list
    width 100%
    text-align left
    border none
    border-top none
    max-height 400px
    overflow-y auto
    border-bottom 1px solid #157977
    .v-autocomplete-list-item
      cursor pointer
      background-color #fff
      padding 10px
      border-bottom 1px solid #157977
      border-left 1px solid #157977
      border-right 1px solid #157977
      &:last-child
        border-bottom none
      &:hover
        background-color #eee
      abbr
        opacity 0.8
        font-size 0.8em
        display block
        font-family sans-serif
</style>