var placeSearch, autocomplete, geocoder, lat, lng;
var componentForm = {
  street_number: 'short_name',
  route: 'long_name',
  locality: 'long_name',
  administrative_area_level_1: 'short_name',
  country: 'long_name',
  postal_code: 'short_name'
};

function initialize() {
  autocomplete = new google.maps.places.Autocomplete((document.getElementById('geo-location')),{ types: [] });
  geocoder = new google.maps.Geocoder();
  google.maps.event.addListener(autocomplete, 'place_changed', function() {
    console.log("Here...");
    var place = autocomplete.getPlace();
    $('#geo-location').val(place.formatted_address);
    placeSearch = place;
    lat = placeSearch.geometry.location.lat();
    lng = placeSearch.geometry.location.lng();
  });
}

function geolocate() {
  if (navigator.geolocation) {
    initialize();
    navigator.geolocation.getCurrentPosition(function(position) {
      var geolocation = new google.maps.LatLng(
          position.coords.latitude, position.coords.longitude);
      autocomplete.setBounds(new google.maps.LatLngBounds(geolocation,
          geolocation));
    });
  }
}

function codeAddress() {
  var address = document.getElementById("geo-location").value;
  geocoder.geocode( { 'address': address}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      var geolocation = results[0].geometry.location;
      lat = geolocation.lat();
      lng = geolocation.lng();
    } else {
      alert("Geocode was not successful for the following reason: " + status);
    }
  });
}