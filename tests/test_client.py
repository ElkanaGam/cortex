import pytest
from pathlib import Path
import struct
import sys
from pytest_httpserver import HTTPServer
from werkzeug.datastructures import MultiDict as mDict
from client import Client as cl, upload_sample
from flask import Flask, request
import requests
import multiprocessing
from click.testing import CliRunner
from project_utils.dataparser import Parser 
from project_utils import cortex_pb2
runner = CliRunner()

OUTPUT = 'Start reading data from <./tests_data>\nand upload to 127.0.0.1, at 8000 ....\n\n200 code\n200 code\n'

def create_client():
    c = cl()     #instaniate new client object
    c.user_id = 12 # set the client user id
    return c


def test_get_param():
    contain_data_query = '?user_id=12&contain_data=yes'
    not_contain_query = '?user_id=12&contain_data=no'
    c = create_client()
    assert contain_data_query == c.get_param(True)
    assert not_contain_query == c.get_param(False)



def test_post(httpserver):
    c = create_client()
    # check post to /snapshot?user_name=12&contain_data=yes
    httpserver.expect_request("/snapshot",query_string='user_id=12&contain_data=yes').respond_with_data('ok')
    assert c.post('hello', True, destination=httpserver.url_for("/snapshot")) == 200
    # check post to /snapshot?user_name=12&contain_data=yes
    httpserver.expect_request("/snapshot",query_string='user_id=12&contain_data=no').respond_with_data("ok")
    assert c.post('hello', False, destination=httpserver.url_for("/snapshot")) == 200



def test_upload(bin_file, capsys, start_server):
    p = start_server
    # success upload case
    response = runner.invoke(upload_sample,['-h','127.0.0.1','-p','8000','./tests_data'])   
    #upload_sample(path='./tests_data', parser=Parser(cortex_pb2, cortex_pb2))
    
    assert response.exit_code == 0
    assert OUTPUT in response.output
    # # file not found case
    # with pytest.raises('FileNotFoundError'):
    #     upload_sample(path='/home/user/not_exist', parser=protocol)
    # # connection failed case
    # with pytest.raises(requests.exceptions.ConnectionError):
    #     upload_sample(path=bin_file,port=5000,parser=protocol)
    # # stop reading the data case
    # with pytest.raises(StopIteration):
    #     upload_sample(path=bin_file, parser=protocol)


class _MokeParser:

    def __init__(self, p_in, p_out):
        self.in_user = p_in.User()
        self.in_snap = p_in.Snapshot()
        self.out = p_out

    def deserialize(self, data_bytes, message_type='snapshot'):
        if message_type == 'snapshot':
            return self.in_snap.ParseFromString(data_bytes)
        else:
            return self.in_user.ParseFromString(data_bytes)

    def serialize(self, data_message, message_type='snapshot'):
        if message_type == 'snapshot':
            return data_message.encode('utf-8')
        else:
            return data_message.data.encode('utf-8')

class user_data:

    def __init__(self, data, i_d):
        self.data = data
        self.user_id = i_d


class _MokeProtocol:

    class User:

        def ParseFromString(self, bytes_data):
            return  user_data(bytes_data.decode('utf-8'), 12)

        def SerializeToString(self, data):
            return data.encode('utf-8')

    class Snapshot:

        def ParseFromString(self, bytes_data):
            return bytes_data.decode('utf-8')

        def SerializeToString(self, data):
            return data.encode('utf-8')

@pytest.fixture()
def bin_file(tmp_path):
    p = Path(tmp_path) / "bin_file"
    with open (p, 'wb') as f:
        massage = b'hello world'
        length = len(massage)
        d = struct.pack('I', length)
        d = bytearray(d)
        d += massage
        f.write(d)
        massage = b'goodbye world'
        length = len(massage)
        d = struct.pack('I', length)
        d = bytearray(d)
        d += massage
        f.write(d)
    return  p



def echoserver():
    app = Flask(__name__)
    @app.route("/")
    def hello():
        return '<form action="/echo" method="POST"><input name="text"><input type="submit" value="Echo"></form>'

    @app.route("/snapshot", methods=['POST'])
    def echo():
        return  'OK'

    app.run(host='127.0.0.1', port =8000)

@pytest.fixture(autouse=True, scope='session')
def start_server():
    p = multiprocessing.Process(target=echoserver)
    p.start()
    yield
    print('terminate')
   

    