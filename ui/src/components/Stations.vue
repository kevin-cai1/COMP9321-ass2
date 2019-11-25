<template>
    <div>
        <h2>Stations in {{ result.Requested_Loc }}</h2>
        <div class="row">
            <div class="col-md-3"/>
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
            <div class="col-md-3"/>
            <b-table striped hover :items="result.Stations"></b-table>
        </div>
    </div>
</template>
<script>
import Vue from 'vue';
import {gmapApi} from 'vue2-google-maps';

export default {
    name: 'Stations',
    props: {
        result: Object
    },
    methods: {
        createMarker(place, map, name) {
            var marker = new google.maps.Marker({
                map: map,
                position: place.geometry.location,
                title: name,
                name: name
            });

            google.maps.event.addListener(marker, 'click', function() {
                var infowindow = new google.maps.InfoWindow();
                infowindow.setContent(name);
                infowindow.open(map, marker);
            })
        }
    },
    mounted: function() {
        Vue.$gmapApiPromiseLazy().then(() => {
            
            this.$refs.gmap.$mapPromise.then((map) => { 
                var placesService = new google.maps.places.PlacesService(map);
                for (var i = 0; i < this.result.Stations.length; i++) {
                    const station = this.result.Stations[i]
                    placesService.findPlaceFromQuery({
                        query: station.Station_Address,
                        fields: ['name', 'geometry']
                    }, (results, status) => {
                        if (status === google.maps.places.PlacesServiceStatus.OK) {
                            this.createMarker(results[0], map, station.Station_Name)
                            if (i === this.result.Stations.length) {
                                map.setCenter(results[0].geometry.location)
                                map.setZoom(11)
                            }
                        }
                    })
                }
                
            })
        })
    },
}
</script>