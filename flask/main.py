import sys
from flask import Flask, request, jsonify, send_file, url_for, redirect
from tsadf.main import detect

app = Flask(__name__)

@app.route("/")
def data():
    ts = request.args.get('t')
    freq = request.args.get('f')
    method = request.args.get('m')
    # seas = request.args.get('s')
    lower = request.args.get('l')
    higher = request.args.get('b')
    plot = request.args.get('p')
    if not ts or not freq:
        return "Incomplete request: please provide (at least) time series file and time series frequency."

    # p = Process(target=detect, args=('tsadf/sample_data.csv', 96, 'interactive', 0, 100000,))
    # p.start()
    # p.join()


    return jsonify(detect(ts, freq, method, lower, higher))

    # response = send_file(tempFileObj, as_attachment=True, attachment_filename='detailed_plot.png')

@app.route("/interactive", methods=['POST'])
def send_bool():
    boolean = request.form['boolean']
    print(boolean)
    return redirect(url_for('data'))

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
