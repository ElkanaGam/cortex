from project_utils.publisher import Publisher
from project_utils.queue_message import MessageQueue


class Consumer:
    '''create connection to message queue from the consumer end'''

    def __init__(self,  ex_name,queue=MessageQueue, host='127.0.0.1'):
        '''
        :param ex_name: the exchange name to be listened
        :param routing_key: the queue name , default = '', cahnge in case roouting_key = ''
        :param queue: the message queue object , responsible to handle and create the queue
        :param host: host for the queue
        '''
        # create the connection
        self.queue = queue(ex_name,  host)

    def create_connection(self, ex_type= 'direct'):
        self.queue.build_connection(ex_type)

    def bind_connection(self, routing_key):
        self.queue.bind_connection(routing_key)

    def consume_data(self, func):
        '''
        consume the data from specific queue which was bind to the exchange
        :param func: function to handle the data
        :return: None
        '''
        self.queue.consume(func)

