const {ipcRenderer, shell} = require('electron')

ipcRenderer.on('preview', (event, socket, img) => {
  document.getElementById('plot').src = "data:image/png;base64, " + img.toString();

	document.getElementById('close-modal').onclick = function() {
	  ipcRenderer.send('close-modal')
	}
})
