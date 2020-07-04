const {ipcRenderer, shell} = require('electron')
const {PythonShell} = require('python-shell')

document.getElementById('boolean-no').onclick = function() {
  var boolean = 'n'
  ipcRenderer.send('boolean', boolean)
}

document.getElementById('boolean-yes').onclick = function() {
  var boolean = 'y'
  ipcRenderer.send('boolean', boolean)
}

document.getElementById('close-modal').onclick = function() {
  ipcRenderer.send('close-modal')
}
