from project_utils.queue_message import MessageQueue
import json

class Publisher:
    '''create connection to message queue from the publisher end'''
    def __init__(self, ex_name, queue=MessageQueue, host='127.0.0.1'):
        '''

        :param ex_name: the exchange name
        :param queue: the message queue object , responsible to handle and create the queue
        :param host: host for the queue
        '''
        #create the connection
        self.queue = queue(ex_name,  host)


    def publish_data(self, data ,routing_key,ex_type='direct'):
        '''
        publish the data as json
        :param data: pyhton dict
        :return: None
        '''
        bin_data = json.dumps(data)
        self.queue.build_connection(ex_type)
        self.queue.publish_message(bin_data, routing_key)

    def stop_publish(self):
        '''stop the connection for the excahnge'''
        self.queue.close_connection()

def data_object():
    '''return fake object to pass into the queueu'''


    data = {'user_id': 12, 'datetime': 1001, 'trans_x': 10, 'trans_y': 11, 'trans_z': 12,
            'rotat_x': 5, 'rotat_y': 6, 'rotat_z': 7, 'rotat_w': 8,
            'img_size':(100,100), 'color_img_path':'',
                'd_img_size':(50,50), 'depth_img_path':'',
                'hunger':1, 'thirst':0,'exhaustion':2, 'happiness':-1}
    return data

if __name__ == '__main__':
    p = Publisher('data_exchange')
    data = data_object()
    p.publish_data(data, 'data')


