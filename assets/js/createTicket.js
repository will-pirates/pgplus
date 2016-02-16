$(document).ready(function() {
$.get('/people/get', function(data){
  var people = JSON.parse(data);
  populatePeople(people.engineers, '#engineer');
  populatePeople(people.customers, '#customer');
});

$.get('/tags/get', function(data){
  var tags = JSON.parse(data);
  populatePeople(tags, '#issue-type');
});

$('form input').keydown(function(event){
  if(event.keyCode == 13) {
    event.preventDefault();
    return false;
  }
});

$('#load-relevant-people').click(function(){
  $.get("/tickets/get_people", { 
    'tag': $('#issue-type').val()
  }).done(function(data) {
    var circlePeople = JSON.parse(data);
    load(circlePeople);
  });
  return false;
});

$('.add-item-button').click(function(event) {
  return addItem(event, $(this).parent().find('.item').attr('id'));
});
});

function populatePeople(people, elem_id){
for(idx in people) {
  var person = people[idx];
  var option = document.createElement("option");
  option.value = person[1];
  option.innerHTML = person[0];
  $(elem_id).append(option);
}
}

function submitTicket() {
$(".spinner-container").show();
$.post( "/tickets/create", { 
  'lat': placeSearch.geometry.location.lat(), 
  'lng': placeSearch.geometry.location.lng(),
  'issue-type': $('#issue-type').val(),
  'equipments': getItems('equipments'),
  'engineer': $('#engineer').val(),
  'dispatcher': $('#dispatcher').val(),
  'other_engineers': $('#other-engineers').val().join('#$#'),
  'notes': getItems('customernotes'),
  'documents' : getItems('ticketdocuments'),
  'location_text': $('#geo-location').val(), 
  'services': getItems('services')
}).done(function(data) {
  alert( "Successfully added ticket with ID: "+data.ticket_id);
  $(".spinner-container").hide();
});
}

function addItem(event, item) {
event.preventDefault();
var p = document.createElement("p");
p.innerHTML = $('#'+item).val();
$('#'+item).parent().find(".itemslist").append(p);
$('#'+item).val('');
$('#'+item).parent().find(".item-part").val('');
return false;
}

function getItems(item_id) {
var items = '';
$('#'+item_id+' .itemslist p').each(function(){ items = $(this).text() + ' #$# ' + items;});
items = items.substring(0,items.lastIndexOf(' #$# '));
return items;
}