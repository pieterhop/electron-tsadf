# TSADF - An anomaly detection application

TSADF is a cross-platform desktop application which can be used for detecting anomalies in time series data. The application is based on the anomaly detection framework developed by [Dr. Ilias Gerostathopoulos](https://github.com/iliasger) and colleagues, and serves mainly as a intuitive user-interface for this framework. Additional functionalities on this framework included in this application are a time series interval check and a preview functionality. See the instructions below for installing this application.

## Install instructions

To clone and run this repository you'll need [Git](https://git-scm.com) and [Node.js](https://nodejs.org/en/download/) (which comes with [npm](http://npmjs.com)) installed on your computer. From your command line:

```bash
# Install flask
pip install flask
# Clone this repository
git clone https://github.com/pieterhop/electron-tsadf
# Go into the repository
cd ~/electron-tsadf
# Install dependencies
npm install
# Start flask web-server
python flask/main.py
# Run the app
# open new window
npm start
```

Note: use the provided time series file (sample_data.csv) for testing.

Note: If you're using Linux Bash for Windows, [see this guide](https://www.howtogeek.com/261575/how-to-run-graphical-linux-desktop-applications-from-windows-10s-bash-shell/) or use `node` from the command prompt.

## Contact

If you run into any problems, feel free to contact me any time. Please see the contact details on my profile.

## License

This project is licensed under an MIT license
