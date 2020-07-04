const {ipcRenderer, shell} = require('electron')

document.getElementById('start-tsadf-button').onclick = function() {
  var invalid = false
  var data = {"file": ""}

  if (document.getElementById('select-file').files[0] != undefined) {
    data["file"] = document.getElementById('select-file').files[0].path
  }
  // temporary
  data["file"] = "/Users/pieterhop/Documents/VU/Jaar 4/Semester 2/Thesis/Prototype/tsadf/flask/tsadf/sample_data.csv"
  data["lowerbound"]  = document.getElementById('lower-bound').value
  data["upperbound"]  = document.getElementById('upper-bound').value
  data["tsf_amount"] = document.getElementById('tsf-amount').value
  data["tsf_unit"] = document.getElementById('tsf-unit').value
  data["seasonality"] = document.getElementById('seasonality').value
  data["tsm"] = document.getElementById('tsm').value

  for (key in data) {
    if (data[key] == "") {
      alert('Please fill in all required fields.')
      invalid = true
      return
    }
  }

  if (invalid == false) {
    ipcRenderer.send('start-tsadf', data)
  }
}

var desc = {
  "file": "Select an input file to get started. The data point features should be [time] and [value], where the time time stamps should be in a standard format and have equal time intervals. The supported format is .csv",
  "avr": "Select an acceptable value range for the provided time series. Values outside of this range will be ignored.",
  "tsf": "Select the time series frequency for the provided time series. The frequency should represent the number of time series data points in one seasonal pattern.",
  "seas": "Select the seasonality of the provided time series. The default is automatic. This option will detect the seasonality of the provided data.",
  "threshold": "Select the preferred threshold selection method for detecting anomalies. Automatic mode will automatically detect the anomalies in your time series. Interactive threshold selection is an advanced method which required manual labeling of data points in time series. This may require knowledge of the time series domain. The default method is automatic.",
  "buttons": "Click the start button to begin the anomaly detection process. Please wait. This may take a while.</p><p>Press the preview button to preview a sample of the time series in your input file."
}

document.getElementById("file").onmouseenter = function() {mouseEnter("file")};
document.getElementById("avr").onmouseenter = function() {mouseEnter("avr")};
document.getElementById("tsf").onmouseenter = function() {mouseEnter("tsf")};
document.getElementById("seas").onmouseenter = function() {mouseEnter("seas")};
document.getElementById("threshold").onmouseenter = function() {mouseEnter("threshold")};
document.getElementById("buttons").onmouseenter = function() {mouseEnter("buttons")};

function mouseEnter(id) {
  document.getElementById("help-desc").innerHTML = desc[id];
}
