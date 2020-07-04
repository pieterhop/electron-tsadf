const {ipcRenderer, shell} = require('electron')

ipcRenderer.on('results', (event, results, data) => {
  document.getElementById('file').innerHTML = data.file;
  document.getElementById('lowerbound').innerHTML = data.lowerbound;
  document.getElementById('upperbound').innerHTML = data.upperbound;
  document.getElementById('tsf').innerHTML = data.tsf_amount + " " + data.tsf_unit;
  document.getElementById('seasonality').innerHTML = data.seasonality[0].toUpperCase() + data.seasonality.slice(1);
  document.getElementById('tsm').innerHTML = data.tsm[0].toUpperCase() + data.tsm.slice(1);

  document.getElementById('pd').innerHTML = results.pd_anomaly;
  document.getElementById('dd').innerHTML = results.dd_anomaly;
  document.getElementById('common').innerHTML = results.common_anomaly;
  document.getElementById('extreme').innerHTML = results.extreme_anomalies;
})

document.getElementById('return-main').onclick = function() {
  ipcRenderer.send('return-main')
}
