const {app, BrowserWindow, ipcMain, dialog} = require('electron')
const path = require('path')
const http = require('http')
const querystring = require('querystring');
const WebSocket = require('ws');

var mainWindow
var detectWindow

function createMainWindow () {
  mainWindow = new BrowserWindow({
    width: 1920,
    height: 1280,
    backgroundColor: '#383A3C',
    fullscreenable: true,
    webPreferences: {
      nodeIntegration: true
    },
    icon: path.join(__dirname, 'Icon/Icon.icns')
  })
  mainWindow.loadFile('src/index.html')
}
app.whenReady().then(createMainWindow)

function loadResults(results, data) {
  mainWindow.loadFile('src/results.html')
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.send('results', results, data)
  })
}

function refreshInteractive(socket, img) {
  detectWindow.loadFile('src/interactive.html')
  detectWindow.webContents.on('did-finish-load', () => {
    detectWindow.webContents.send('image', socket, img)
  })
}

ipcMain.on('start-tsadf', (event, data) => {
  detectWindow = new BrowserWindow({
    width: 800,
    height: 550,
    parent: mainWindow,
    modal: true,
    show: false,
    backgroundColor: '#383A3C',
    webPreferences: {
      nodeIntegration: true
    }
  })
  detectWindow.loadFile('src/detect.html')
  detectWindow.once('ready-to-show', () => {
    detectWindow.show()
  })

  const parameters = {
  	t: data.file,
    f: 96,
  	m: data.tsm,
    l: data.lowerbound,
    b: data.upperbound
  }

  if (data.tsm == 'automatic') {
    callback = function(response) {
      console.log('started auto-detect mode');
      var results = '';

      response.on('data', function (chunk) {
        results += chunk;
      });

      response.on('end', function () {
        console.log(results);
        loadResults(JSON.parse(results), data)
        detectWindow.close()
        console.log('finished');
      });
    }
    request = http.request(auto_options, callback).end();

  } else {
    socket = new WebSocket("ws://localhost:4567", { perMessageDeflate: false });
    console.log("Connection established");

    setTimeout(() => {
      socket.send(JSON.stringify(data));
      console.log("Arguments send...");
    }, 200);

    socket.onmessage = function (event) {
      if (Buffer.isBuffer(event.data)) {
        console.log("Image received!");
        // console.log(event.data.toString());
      	refreshInteractive(socket, event.data)
      } else {
        console.log("Results received!");
        loadResults(JSON.parse(event.data), data)
        detectWindow.close()
      }
    }

    ipcMain.on('boolean', (event, boolean) => {
      socket.send(boolean)
    })
  }
})

ipcMain.on('close-modal', (event) => {
  console.log('Process canceled');
  detectWindow.close()
})

ipcMain.on('return-main', (event) => {
  mainWindow.loadFile('src/index.html')
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })
})

ipcMain.on('plot-preview', (event) => {
  console.log('test');
})

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', function () {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})
