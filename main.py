from flask import Flask, render_template, send_from_directory

app = Flask(__name__,static_url_path='')


@app.route('/')
def hello_world():
    # return render_template('index.html')
    return send_from_directory('','index.html')

if __name__ == '__main__':
    app.run(debug=True)
