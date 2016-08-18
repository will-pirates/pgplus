'use strict'
/* eslint no-undef:0 */
/* eslint strict:0 */

// const { topTypes, topWords, codesNames, problemCodes, topCustomerTypes } = window

$('.resultColumn').hide()
$('#stationLabel').hide()

const nameTags = Object.keys(codesNames).reduce((arr, code) => {
  arr.push({
    label: codesNames[code],
    value: code,
  })
  return arr
}, [])

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

$('#customerNameAutocomplete').autocomplete({
  source: nameTags,
  delay: 0,
  select: getStationsResults,
})

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
}