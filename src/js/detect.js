const {ipcRenderer, shell} = require('electron')

document.getElementById('close-modal').onclick = function() {
  ipcRenderer.send('close-modal')
}
