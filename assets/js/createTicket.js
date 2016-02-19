var job_deets = {};

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

  $('.circle-parameter').change(function(){ return circleParameterChanged();});

  $('#job-id').change(function(){ return jobIDChanged();});

  $('.add-item-button').click(function(event) {
    var res = addItem($(this).parent().find('.item').attr('id'), null, event);
    if($(this).hasClass('circle-parameter')) {
      circleParameterChanged();
    }
    return res;
  });

  $('#create-ticket-submit').click(function(event) {
    submitTicket();
    return false;
  });
});

function jobIDChanged() {
  reset_form();
  geolocate();
  $.get("/tickets/get_job_deets", { 
    'job-id': $('#job-id').val()
  }).done(function(data) {
    console.log(data);
    job_deets = JSON.parse(data);
    $('#geo-location').val(job_deets.location.addr);
    codeAddress();
    $('#issue-type').val(job_deets.issue.type);
    $('#issue-type').change();
    for(var i in job_deets.equipments) {
      addItem('equipments', job_deets.equipments[i]);
    }
    $('#equipments').collapse();
    for(var i in job_deets.services) {
      addItem('services', job_deets.services[i]);
    }
    $('#services').collapse();
    $('#engineer').val(job_deets.engineer.id);
    $('#customer').val(job_deets.customer.id);
    for(var i in job_deets.notes) {
      addItem('customernotes', job_deets.notes[i]);
    }
    $('#customernotes').collapse();
    circleParameterChanged();
    for(var i in job_deets.documents) {
      addItem('ticketdocuments', job_deets.documents[i]);
    }
    $('#ticketdocuments').collapse();
  });
  return false;
}

function reset_form() {
  $('#geo-location').val('');
  $('#issue-type').val('-1');
  $('#issue-type').change();
  $('#equipments .itemslist').empty();
  $('#services .itemslist').empty();
  $('#engineer').val('-1');
  $('#customer').val('-1');
  $('#customernotes .itemslist').empty();
  $('#ticketdocuments .itemslist').empty();
}

function circleParameterChanged() {
  $.get("/tickets/get_people", { 
    'tag': $('#issue-type').val(),
    'notes': getItems('customernotes')
  }).done(function(data) {
    var circlePeople = JSON.parse(data);
    load(circlePeople);
  });
  return false;
}

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
    'lat': lat, 
    'lng': lng,
    'issue-type': $('#issue-type').val(),
    'equipments': getItems('equipments'),
    'engineer': $('#engineer').val(),
    'notes': getItems('customernotes'),
    'documents' : getItems('ticketdocuments'),
    'location_text': $('#geo-location').val(), 
    'services': getItems('services'),
    'customer': [$('#customer').val(), $('#customer option:selected').text()].join(),
    'engineer': [$('#engineer').val(), $('#engineer option:selected').text()].join()
  }).done(function(data) {
    alert( "Successfully added ticket with ID: "+data.ticket_id);
    $(".spinner-container").hide();
  });
}

function addItem(item, value, event) {
  if(event) {
    event.preventDefault();
  }
  var p = document.createElement("p");
  if(value) {
    p.innerHTML = value;
  } else {
    p.innerHTML = $('#'+item).val();
    $('#'+item).val('');
    $('#'+item).parent().find(".item-part").val('');
  }
  $('#'+item).parent().find(".itemslist").append(p);
  return false;
}

function getItems(item_id) {
  var items = '';
  $('#'+item_id+' .itemslist p').each(function(){ items = $(this).text() + ' #$# ' + items;});
  items = items.substring(0,items.lastIndexOf(' #$# '));
  return items;
}