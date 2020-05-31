import sys
import logging
import requests
import click
from math import inf
from project_utils.dataparser import Parser
import project_utils.cortex_pb2 as cortex_pb2
import project_utils.utils as utils


UPLOADS_NUM = utils.UPLOADS_NUM  # to limit numbers of uploads
silent = False


class Client:
    '''
    start connection to some desination (host, port)
    '''

    def __init__(self, host='127.0.0.1', port=8000, path='./sample.mind.gz'):
        self.path = path
        self.host = host
        self.port = port
        self.destination = 'http://' + self.host +':'+ str(self.port)
        self.user_id = ''     #will be assign dynamicly
        self.logger = logging.getLogger(__name__)

    def get_param(self, is_contain):
        '''prepare the query param for url request'''
        contain = "yes" if is_contain else "no"
        self.logger.info('prepare the query params')
        return f'?user_id={self.user_id}&contain_data={contain}'

    def post(self, data, is_contain, destination = None):
        '''post request data tqo the desiered url'''
        if destination == None:
            dest = self.destination+'/snapshot'
        else:
            dest = destination
        q_params = self.get_param(is_contain)
        r = requests.post(dest+q_params, data=data)
        self.logger.info(f'send data to {dest+q_params}')

        if r.status_code != 200:
            self.logger.error(f'Exceptiom from post {r.status_code}')
        else:
            self.logger.info('get ok from server')
        return r.status_code


@click.command()
@click.option('--host','-h', default='127.0.0.1',
              help='host of server')
@click.option('--port', '-p', default=8000, help='port of server')
@click.argument('path')
def upload_sample(host='127.0.0.1', port=8000, path='sample.mind', parser=Parser(cortex_pb2, cortex_pb2)):
    '''
    post parsed data to the destination
    parser using protobuf protocol as default
    
    :param host: host of http server destonation 
    :param port: port of http server destonation 
    :param path: path to the data should be uploaded
    :param parser: object to serialze the data, default is protobuf

    '''
    main_logger = utils.create_logger('logs/client.log')
    print(f'Start reading data from <{path}>\n'
          f'and upload to {host}, at {port} ....\n')
    # get the binnary data if path is to compress data
    bin_path = utils.get_binary_path(path)
    reader = utils.Reader(bin_path)
    client = Client(host, port)
    try:
        main_logger.info(f'start reading data from {path}')
        r = reader.read_file()
        data = next(r)
        # user data part
        deserializes_data = parser.deserialize(data, message_type='user')
        # fix the user name so that the server will associate the data to the user
        client.user_id = deserializes_data.user_id
        res = client.post(parser.serialize(deserializes_data, message_type='user'), False)
        if not silent:
            print(res, 'code')
        if res != 200: 
            raise requests.exceptions.ConnectionError
        main_logger.info(f'user data post with {res} status code')
        # starting reading data and upload snapshots        
        data = next(r)
        i = 0       
        while i < UPLOADS_NUM: 
            deserializes_data = parser.deserialize(data, message_type='snapshot')
            res = client.post(parser.serialize(deserializes_data), True)
            main_logger.info(f'snapshot  #{i} data post with {res} status code')
            if res != 200: 
                raise requests.exceptions.ConnectionError
            if not silent:
                print('success upload!')
            data = next(r)
            i+=1
    except requests.exceptions.ConnectionError:
        main_logger.exception('Connection Error. closing', exc_info=False)
        return
    except FileNotFoundError as e:
        main_logger.exception('File not found')
        print(e)
    except StopIteration as e:
        main_logger.info("End of data to be read. close connection")
        print("End of data to be read. close connection")

@click.group()
def main():
    pass
main.add_command(upload_sample)

if __name__ =='__main__':
    main()