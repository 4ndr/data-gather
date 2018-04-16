
var mymap;

function buildMap(lat = 0.01, lon = -0.01, viewLevel = 2) {
    //plot a blanket map
    mymap = L.map('mapid').setView([lat, lon], viewLevel);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets',
        accessToken: 'pk.eyJ1IjoiYW5kcmVwbCIsImEiOiJjaXVnNzZmYmEwMGZyMnlueXMxZjA3NXJnIn0.0zKGPE-sI6MuPRlYlpMLPA'
    }).addTo(mymap);
}


function plotSmartCitizen(jsonData) {
    var markerClusters = L.markerClusterGroup();
    for (var i = 0; i < jsonData.length; i++) {

        var latitude = jsonData[i]['data']['location']['latitude'];
        var longitude = jsonData[i]['data']['location']['longitude'];

        if ((latitude != null) && (longitude != null)){

            var sensors = '';
            sensors += '<p>' + "Temperature" + ': ' + jsonData[i]['data']['sensors'][2]['value'] + '</p>';
            sensors += '<p>' + "Humidity" + ': ' + jsonData[i]['data']['sensors'][1]['value'] + '</p>';
            sensors += '<p>' + "no2" + ': ' + jsonData[i]['data']['sensors'][3]['value'] + '</p>';
            sensors += '<p>' + "co" + ': ' + jsonData[i]['data']['sensors'][4]['value'] + '</p>';

            var mymarker = new L.marker(L.latLng(parseFloat(latitude), parseFloat(longitude)), {icon: greenIcon})
            .bindPopup(sensors);

            markerClusters.addLayer(mymarker);
        }
    }
    mymap.addLayer(markerClusters);

}

function plotLASS(jsonData) {
    var markerClusters = L.markerClusterGroup();
    for (var i = 0; i < jsonData['feeds'].length; i++) {
        var latitude = jsonData['feeds'][i]['gps_lat'];
        var longitude = jsonData['feeds'][i]['gps_lon'];

        if ((latitude != null) && (longitude != null)){

            var sensors = '';
            sensors += '<p>' + "sd0" + ': ' + jsonData['feeds'][i]['s_d0'] + '</p>';
            sensors += '<p>' + "sd1" + ': ' + jsonData['feeds'][i]['s_d1'] + '</p>';

            var mymarker = new L.marker(L.latLng(parseFloat(latitude), parseFloat(longitude)),{icon: redIcon})
            .bindPopup(sensors);

            markerClusters.addLayer(mymarker);
        }
    }
    mymap.addLayer(markerClusters);
}

function plotOpenAQ(jsonData) {
    var markerClusters = L.markerClusterGroup();
    for (var i = 0; i < jsonData['results'].length; i++) {

        if (jsonData['results'][i]['coordinates']){

            var sensors = '';
            sensors += '<p>' + jsonData['results'][i]['parameter'] + ': ' + jsonData['results'][i]['value'] + '</p>';

            var mymarker = new L.marker(L.latLng(parseFloat(jsonData['results'][i]['coordinates']['latitude']),
                parseFloat(jsonData['results'][i]['coordinates']['longitude'])),{icon: blueIcon}).bindPopup(sensors);

            markerClusters.addLayer(mymarker);
        }
    }
    mymap.addLayer(markerClusters);
}