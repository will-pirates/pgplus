'use strict'
/* eslint no-undef:0 */
/* eslint strict:0 */

// const { topTypes, topWords, codesNames, problemCodes, topCustomerTypes } = window

$('.resultColumn').hide()
$('#headerLabel').hide()

const callIds = Object.keys(callids).reduce((arr, code) => {
  arr.push({
    label: code,
    value: code,
  })
  return arr
}, [])

const partIds = Object.keys(notes_parts).reduce((arr, code) => {
  arr.push({
    label: code,
    value: code,
  })
  return arr
}, [])
/*
const typeTags = Object.keys(problemCodes).reduce((arr, code) => {
  arr.push({
    label: problemCodes[code],
    value: code,
  })
  return arr
}, [])

$('#issueTypeAutocomplete').autocomplete({
  source: typeTags,
  delay: 0,
  select: function selectFunc(event, ui) {
    $('#stationResults').empty().hide()
    $('.resultColumn').hide()
    $('#issueTypeAutocomplete').val(ui.item.label)
    const code = ui.item.value
    const theseTopStations = topCustomerTypes[code] || {}
    const resultsDOM = $('#stationResults')
    Object.keys(theseTopStations).forEach(station => {
      if (codesNames[station]) {
        resultsDOM.append(
          `<div
            class='stationResult'
            style='cursor: pointer; border: 1px solid lightgrey; padding: 5px'
            data-station=${station}>
            ${codesNames[station]}: ${theseTopStations[station]} occurences
          </div>`
        )
      }
    })
    $('.stationResult').on('click', function(){
      const station = $(this).attr('data-station')
      const fakeUiObject = {
        item: {
          label: codesNames[station],
          value: station
        }
      }
      getStationsResults(null, fakeUiObject)
    })
    $('#stationResults').fadeIn()
    $('#stationLabel').fadeIn()
  },
})
*/
$('#callIDAutoComplete').autocomplete({
  source: callIds,
  delay: 0,
  select: getCallResults,
})

$('#partIDAutoComplete').autocomplete({
  source: partIds,
  delay: 0,
  select: getPartsResults,
})

function getPartsResults(event, ui) {
  $('#sqlAnalysis').empty();
  $('#partIDAutoComplete').val(ui.item.label);
  const partID = ui.item.value;
  var notes = notes_parts[partID];
  $('#headerLabel').fadeIn();
  var notesString = "";
  for (var i = 0; i < notes_parts[partID].length; i++) {
    notesString = notesString + notes_parts[partID][i] + "<br> ";
  }
  $('#sqlAnalysis').append(notesString);
}

function getCallResults(event, ui) {
  $('#sqlAnalysis').empty();
  $('#siteAnalysis').empty();
  $('#techAnalysis').empty();
  $('#callIDAutoComplete').val(ui.item.label);
  const callID = ui.item.value;
  var callDeets = callids[callID];
  $('#headerLabel').fadeIn();
  var partsString = "";
  for (var i = 0; i < callDeets["parts"].length; i++) {
    partsString = partsString + callDeets["parts"][i]["part_name"] + " :: " + callDeets["parts"][i]["part_desc"] + "<br> ";
  }
  var html = "<p><b>Customer:</b> " + callDeets["customer"] + "</p><br><p><b>Technician ID:</b> " + callDeets["technician"] + "</p><br><p><b>Parts used:</b><br> " + partsString + "</p>"
  $('#sqlAnalysis').append(html);
  var allPartsString = "";
  for (var i = 0; i < customers[callDeets["customer"]].length; i++) {
    allPartsString = allPartsString + customers[callDeets["customer"]][i] + "<br> ";
  }
  var custAnalysisHtml = "<p><b>Site history:</b><br> " + allPartsString + "</p>"
  $('#siteAnalysis').append(custAnalysisHtml);

  var allTechsString = "";
  for (var i = 0; i < technicians[callDeets["technician"]].length; i++) {
    allTechsString = allTechsString + technicians[callDeets["technician"]][i] + "<br> ";
  }
  var techAnalysisHtml = "<p><b>Technician's history:</b><br> " + allTechsString + "</p>"
  $('#techAnalysis').append(techAnalysisHtml);
}
/*
function getStationsResults(event, ui) {
  $('.resultColumn').hide()
  $('#wordsresults').empty()
  $('#results').empty()
  $('#customerNameAutocomplete').val(ui.item.label)
  const code = ui.item.value
  const theseTopWords = topWords[code].sort((a, b) => b.frequency - a.frequency)
  const theseTopTypes = topTypes[code]
  const typesToAppend = Object.keys(theseTopTypes)
  .map(type =>
    ({
      code: type,
      count: theseTopTypes[type],
    })
  )
  .sort((a, b) => b.count - a.count)
  .map(obj =>
    ({
      display: problemCodes[obj.code],
      value: obj.count,
    })
  )

  typesToAppend.forEach(obj => {
    if (obj.display) $('#results').append(`<div>${obj.display}: ${obj.value}</div>`)
  })
  
  theseTopWords.forEach(word => {
    $('#wordsresults').append(`<div>${word.word} (${word.frequency} occurences)</div>`)
  })

  $('.resultColumn').fadeIn()
}*/