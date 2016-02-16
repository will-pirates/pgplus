var placeSearch, autocomplete;
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
  google.maps.event.addListener(autocomplete, 'place_changed', function() {
    console.log("Here...");
    var place = autocomplete.getPlace();
    $('#geo-location').val(place.formatted_address);
    placeSearch = place;
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