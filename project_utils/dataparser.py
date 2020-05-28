import logging

class Parser :
    '''
        responsable to deserialize raw bytes data according to
        @protocol_input, and serialize it according to
        @protocol_output
        those protocol can be imported staticly by import declaration
        or dynamic import within the init method
    '''

    def __init__(self, protocol_input, protocol_output):
        self.user_parser = protocol_input.User()
        self.snap_parser = protocol_input.Snapshot()
        self.protocol_out = protocol_output
        self.log = logging.getLogger(__name__)
        self.log.info('data parser created')

    def deserialize(self, data_bytes, message_type='snapshot'):
        '''return an object contains data desrialized by the protocol_input'''
        self.log.info(f'deserializing with {message_type}')
        if message_type == 'snapshot':
            self.snap_parser.ParseFromString(data_bytes)
            return self.snap_parser
        else:
            self.user_parser.ParseFromString(data_bytes)
            return self.user_parser

    def serialize (self, data_message, message_type='snapshot'):
        '''return serialized data bytes according to the protocol_output'''
        self.log.info(f'serializing with {message_type}')
        if message_type == 'snapshot':
            data = self.protocol_out.Snapshot(
                datetime=data_message.datetime,
                pose=data_message.pose,
                color_image=data_message.color_image,
                depth_image=data_message.depth_image,
                feelings=data_message.feelings

            )

        else:

            data = self.protocol_out.User(
                user_id=data_message.user_id,
                username=data_message.username,
                birthday=data_message.birthday,
                gender=data_message.gender

            )

        return data.SerializeToString()



