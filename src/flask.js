const {app, BrowserWindow, ipcMain, dialog} = require('electron')
const path = require('path')
const http = require('http')
const {PythonShell} = require('python-shell')
const querystring = require('querystring');

var mainWindow
var detectWindow
var shell

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

function refreshInteractive() {
  detectWindow.loadFile('src/interactive.html')
  detectWindow.once('ready-to-show', () => {
    detectWindow.show()
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

  const auto_options = {
    hostname: '127.0.0.1',
    port: 5000,
    path: '/?' + querystring.stringify(parameters),
    method: 'GET'
  }

  const int_options = {
    mode: 'text',
    pythonPath: 'python',
    pythonOptions: ['-u'],
    scriptPath: path.join(__dirname, '../flask/tsadf'),
    args: ['-t=' + data.file, '-f=96', '-m=' + data.tsm, '-l=' + data.lowerbound, '-b=' + data.upperbound]
  };

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
    var results = []
    shell = new PythonShell('main.py', int_options)
    console.log('started interactive mode');
    shell.on('message', function (message) {
      results.push(message)
      if (message == 'case') {
        console.log(message);
        refreshInteractive()
        shell.send('y')
      } else if (message == 'finished') {
        console.log(message);
        console.log(results[results.length - 2])
        loadResults(results, data)
        detectWindow.close()
      }
      else {
        console.log(message);
      }
    })
  }
})

ipcMain.on('boolean', (event, boolean) => {
  shell.send(boolean)
})

ipcMain.on('close-modal', (event) => {
  shell.terminate()
  console.log('process terminated');
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
