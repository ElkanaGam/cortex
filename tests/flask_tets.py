from flask import Flask, request
import requests

def echoserver():
    app = Flask(__name__)

    @app.route("/")
    def hello():
        return '<form action="/echo" method="POST"><input name="text"><input type="submit" value="Echo"></form>'

    @app.route("/snapshot", methods=['POST'])
    def echo():
        return request.get_data().decode('utf-8')

    app.run(host='127.0.0.1', port =8000)




if __name__ == '__main__':
    echoserver()

