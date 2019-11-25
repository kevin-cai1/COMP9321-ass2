<template>
    <div>
        <h2>{{ result.Station_Name }}</h2>
        <p><b>Address:</b> {{ result.Station_Address }}</p>
        <p><b>Fuel Type:</b> {{ result.Fuel_Type }}</p>
        <br/>
        <div class="row">
        <div class="col-md-6">
        <GmapMap
            :center='{lat:-33.867, lng:151.195}'
            :zoom="7"
            style="width: 500px; height: 300px"
            align="left"
            ref="gmap"
        >
        </GmapMap>
        </div>
        <div class="col-md-6">
            <GChart
                type="LineChart"
                :data="pricingChartData"
                :options="chartOptions"
            />
        </div>
        </div>
        <br/>
        <b-table striped hover :items="result.Prices"></b-table>
    </div>
</template>
<script>
import Vue from 'vue';
import {gmapApi} from 'vue2-google-maps';
import { GChart } from 'vue-google-charts';

export default {
    name: 'Station',
    props: {
        result: Object
    },
    components: {
        GChart
    },
    methods: {
        createMarker(place, map, name) {
            var marker = new google.maps.Marker({
                map: map,
                position: place.geometry.location,
                title: name,
                name: name
            });
            var infowindow = new google.maps.InfoWindow();
            infowindow.setContent(name);
            infowindow.open(map, marker);
        }
    },
    data: function() {
        var priceMap = this.result.Prices.map(d => Array.from(Object.values(d)))
        priceMap.unshift(["Date", "Price"])
        return {
            pricingChartData: priceMap,
            chartOptions: {
                title: "Pricing over Time",
                subtitle: ""+this.result.Fuel_Type+" pricing over time and predicated."
            }
        }
    },
    mounted: function() {
        Vue.$gmapApiPromiseLazy().then(() => {
            
            this.$refs.gmap.$mapPromise.then((map) => { 
                var placesService = new google.maps.places.PlacesService(map);
                console.log(this.result.Station_Address)
                placesService.findPlaceFromQuery({
                    query: this.result.Station_Address,
                    fields: ['name', 'geometry']
                }, (results, status) => {
                    if (status === google.maps.places.PlacesServiceStatus.OK) {
                        this.createMarker(results[0], map, this.result.Station_Name)
                        map.setCenter(results[0].geometry.location)
                        map.setZoom(10)
                    }
                })
            })
        })
    },
}
</script>