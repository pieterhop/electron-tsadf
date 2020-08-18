const {ipcRenderer, shell} = require('electron')

ipcRenderer.on('image', (event, socket, img) => {
  document.getElementById('plot').src = "data:image/png;base64, " + img.toString();

	document.getElementById('boolean-no').onclick = function() {
	  ipcRenderer.send('boolean', 'no')
	}

	document.getElementById('boolean-yes').onclick = function() {
	  ipcRenderer.send('boolean', 'yes')
	}

	document.getElementById('close-modal').onclick = function() {
	  ipcRenderer.send('close-modal')
	}
})
