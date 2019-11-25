<template>
    <div>
        <h2>{{ result.Station_Name }}</h2>
        <p><b>Address:</b> {{ result.Station_Address }}</p>
        <p><b>Fuel Type:</b> {{ result.Fuel_Type }}</p>
        <br/>
        <b-table striped hover :items="result.Prices"></b-table>
    </div>
</template>
<script>
export default {
    name: 'Station',
    props: {
        result: Object
    }
}
</script>