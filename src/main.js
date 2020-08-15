const {app, BrowserWindow, ipcMain, dialog} = require('electron')
const {PythonShell} = require('python-shell')
const path = require('path')
const reload = require('electron-reload')(__dirname)

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

  let options = {
    mode: 'text',
    pythonPath: 'python',
    pythonOptions: ['-u'],
    scriptPath: path.join(__dirname, 'code'),
    args: ['-t=' + data.file, '-f=96', '-m=' + data.tsm, '-s=' + data.seasonality, '-l=' + data.lowerbound, '-b=' + data.upperbound]
  };

  if (data.tsm == 'automatic') {
    shell = PythonShell.run('main.py', options, function (err, results) {
      console.log('started auto-detect mode');
      loadResults(results, data)
      detectWindow.close()
      console.log('finished');
    })
  } else {
    var results = []
    shell = new PythonShell('main.py', options)
    console.log('started interactive mode');
    shell.on('message', function (message) {
      results.push(message)
      if (message == 'case') {
        console.log(message);
        refreshInteractive()
      } else if (message == 'finished') {
        console.log(message);
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


// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', function () {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
