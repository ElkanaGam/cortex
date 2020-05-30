import sys
import logging
from flask import Flask , request, Response
from project_utils.dataparser import Parser
import project_utils.cortex_pb2 as cortex_pb2
import project_utils.utils as utils
import project_utils.publisher as publisher
import click



app = Flask(__name__)
logger = utils.create_logger('logs/server.log')
silent = False

#get the user / snapshots data from user
@app.route('/snapshot', methods=['POST'])
def serve_data():
    '''
        recieve the data from client
        query params are:
        @user_name to associate the data to the proper user
        @contain_data if this request conatian also snapshot data
    '''
    if request.method == 'POST':
        # extract the query params
        user_id = request.args.get('user_id')         
        contain_data = request.args.get('contain_data')
        logger.info(f'data has coming to {user_id} and {contain_data} data ')
        # extract the payload
        data = request.get_data()
        status_code = Response(status=200)
        if contain_data == 'no':
            try:
                user_stuff(data, app.config['parser'],app.config['publisher'])
            except:
                logger.exception('some trouble while publishing user data')
                status_code = Response(status=500)
        else:
            try:
                data_stuff(user_id, data,app.config['parser'],app.config['publisher'])
            except:
                logger.exception('some trouble while publishing snapsot  data')
                status_code = Response(status=500)
        logger.info(status_code)
        return status_code


def user_stuff( data, parser, publish_func):
    try:
        user = parser.deserialize(data, message_type='user')
        u_name, u_id, u_birthday, u_gender =  user.username, user.user_id, user.birthday, user.gender
        data = {'name':u_name,"user_id":u_id,
                "birthdate":u_birthday, "gender":u_gender}
        logger.info('publish user data')
        publish_func(data, utils.USERS_RT_KEY)
        logger.info('finish to publish user data')
        if not silent:
            print(data)
    except Exception as e:
        raise e



def data_stuff(user_id, data, parser,publish_func):
    '''
        handle the snapshot data and route it to the @name in Path.cwd() /  name directory 
    '''
    try:

        snapshot = parser.deserialize(data)
        # orginaize the data in a dictionary
        data = utils.snapshots_to_dict(snapshot, user_id)
        if not silent:
            print(data)
        logger.info('publish snapshot data')
        publish_func(data, utils.SERVER_ROUTING_KEY)
        logger.info('finish to publish snapshot data')
    except Exception as e:
        raise e


def init_queue(message_queue_scheme):
    '''Instantiate message queue in a host according to shceme'''
    name, host, port = message_queue_scheme.split(':')
    logger.info(f'{host} {name} {port}')
    if name != 'rabbitmq':
        print('This Message Queue is not suppotred')
        raise Exception
    else:
        host = host[2:]
        snapshot_publisher = publisher.Publisher(utils.SERVER_EXCHANGE, host=host)
        return snapshot_publisher.publish_data


@click.command()
@click.option('--host','-h', default='127.0.0.1',
              help='host of server')
@click.option('--port', '-p', default=8000, help='port of server')
@click.argument('message_queue')
def run_server(host = '127.0.0.1', port = 8000, publish = print, message_queue=None):
    '''Get the snapshots and publish them to message-queue

        :param host: host for listening
        :param port: port for listening
        :param message_queue': url for queue to deliver data into 
        '''
    logger.info(f'Start serving at http://{host}:{port}')
    # set the publish function for the sever
    if message_queue is None:
        app.config['publisher'] = publish
    else:
        try:
            app.config['publisher'] = init_queue(message_queue)
        except:
            print('Can not connect to message Queue. Closing...')
            return
    # set the parser of the data
    parser = Parser(cortex_pb2, cortex_pb2)
    app.config['parser'] = parser
    print(f'Start serving at http://{host}:{port}')
    app.run(host = host, port = port)

@click.group()
def main():
    pass

main.add_command(run_server)

if __name__ == '__main__':
    main()

