const {ipcRenderer, shell} = require('electron')
const {PythonShell} = require('python-shell')

document.getElementById('close-modal').onclick = function() {
  ipcRenderer.send('close-modal')
}
