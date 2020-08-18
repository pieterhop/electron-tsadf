const {ipcRenderer, shell} = require('electron')

document.getElementById('boolean-no').onclick = function() {
  websocket.send("no");
	reset();
}

document.getElementById('boolean-yes').onclick = function() {
  websocket.send("yes");
	reset();
}

document.getElementById('close-modal').onclick = function() {
  ipcRenderer.send('close-modal')
}
