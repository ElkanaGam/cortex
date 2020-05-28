import pika
import logging

class MessageQueue:

    '''create connection to pika message queue that allow
        publishing and consuming data'''

    def __init__(self, exchange_name,  host='127.0.0.1'):
        '''

        :param exchange_name: the exchange name in the connection
        :param routing_key: default ='', change it if exchange_name is empty
        :param host: the host of the rabbuit mq connection
        also automaticly set the queue name to be ''. it will be set dinamycly
        if bind connection wiil be called
               '''
    
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.ex_name = exchange_name
        self.queue_name = ''
        self.logger = logging.getLogger(__name__)

    def build_connection(self, ex_type='direct'):
        '''create the specific exchange to publish and consume the data'''
        self.channel.exchange_declare(exchange=self.ex_name,
                                      exchange_type=ex_type)
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = result.method.queue
        self.logger.info(f'establish message queue ')

    def bind_connection(self, routing_key):
        '''
            to consume the data create specific queue within the excahnge
            and consume the data through it, and bind it to the exchange
        '''
        self.logger.info(f'bind connection at{routing_key}')
        self.channel.queue_bind(
            exchange=self.ex_name, queue=self.queue_name, routing_key=routing_key)

    def consume(self, callback):
        '''
        consume the data
        :param callback the function which recive the data from the excahnge and handle it
        :return: None
        '''
        self.logger.info('Start consuming')
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def publish_message(self, message, routing_key):
        '''

        :param routing_key: the route of the message
        :param message: the message to pass to the excahnge
        :return: None
        '''
        self.logger.info('Start publishing')
        self.channel.basic_publish(
            exchange=self.ex_name, routing_key=routing_key, body=message)



    def close_connection(self):
        '''close the connection for the excahge'''
        self.logger.info(f'stop connection at {self.channel} ')
        self.connection.close()





