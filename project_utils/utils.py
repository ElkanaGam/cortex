from math import inf
import logging
# zip files imports
import gzip
import shutil
# read binary files imports
import struct
# snapshots handlers import
import json
from pathlib import Path
import  project_utils.imagehandler as Handler

# program constants

IMAGE_DIR = './static/images'
UPLOADS_NUM = inf
logger  = logging.getLogger(__name__)
SERVER_EXCHANGE = 'data_exchange'
SERVER_ROUTING_KEY = 'data'
USERS_RT_KEY = 'users'
SILENT_MODE = True
parsers_modules = ['parser_list']

###############################
#
# Snapshots handlers section
#
###############################
def _convert_to_list(proto_obj, file_target=None):
    '''Insert protobuf elemnt's data to file if file target specified
        otherwise return it as list to be iterable'''
    if file_target == None:
        data = []
        try:
            for i in proto_obj:
                data.append(i)
            return data
        except Exception as e:
            print ('some trouble ->> ', e )
    else:
        try:
            with open(file_target, 'w') as f:
                for i in proto_obj:
                    f.write(str(i))
                    f.write('\n')
        except Exception as e:
            print ('some trouble ->> ', e )



def snap_obj(path, data):
    with open (path , 'wb') as f:
        json.dump(data, f)

def snapshots_to_dict(snapshot, user_id):
    '''Serialize user_id snapshot data to python dict '''
    pose_trans = snapshot.pose.translation
    pose_rot = snapshot.pose.rotation
    cols = ['trans_' + c for c in ['x', 'y', 'z']] + ['rot_' + c for c in ['x', 'y',
                                                                             'z', 'w']]
    vals = [pose_trans.x, pose_trans.y, pose_trans.z, pose_rot.x, pose_rot.y,
            pose_rot.z, pose_rot.w]
    datetime = snapshot.datetime
    img_size = (snapshot.color_image.width, snapshot.color_image.height)
    img_data = snapshot.color_image.data
    d_img_size = ( snapshot.depth_image.height,snapshot.depth_image.width)
    d_img_data = snapshot.depth_image.data
    feelings_cols = ['hunger', 'thirst','exhaustion', 'happiness']
    feelings_vals = [snapshot.feelings.hunger, snapshot.feelings.thirst,
                     snapshot.feelings.exhaustion, snapshot.feelings.happiness]
    position_data = dict(zip(cols, vals))
    feelings_data = dict(zip(feelings_cols, feelings_vals))
    data = {**position_data, **feelings_data}
    data['datetime'] = datetime
    data['img_size'] = img_size
    data['d_img_size'] = d_img_size
    d_img_data = _convert_to_list(d_img_data)
    data['user_id'] = user_id
    p = Path(IMAGE_DIR) /str(user_id)
    p.mkdir(exist_ok=True)
    handler = Handler.ImageHandler(p)
    data['color_img_path'] = handler.save_binary_color(datetime,  img_size, img_data)
    data['depth_img_path'] = handler.save_binary_depth(datetime,  d_img_size, d_img_data)
    return data













#########################################
#
#Binary files, files  handler section
#
#########################################


##unzip binary file

def _create_path(path):
    '''
    create the path to the decompressed data file
    :param path with zip extension:
    :return: path with out extension
    '''
    p = path.split('.')[:2]
    logger.info(f'the path to  data file is {p[0]}.{p[1]}')
    return f'{p[0]}.{p[1]}'


def _zipped(path):
    '''
    return if path is point to compressed file
    :param path:
    :return: True iff extenion implies compressed data
    '''
    zipped_extensions = {'gz', 'zip'}
    suffix = str(path).split('.')[-1:][0]
    return suffix  in zipped_extensions


def get_binary_path(path):
    '''
        extract compressed data if needed
    :param path:
    :return: path to binary data
    '''
    if not _zipped(path):
        logger.info('path is already unzip')
        return path
    else:
        logger.info('path is zipped')
        bin_file_path = _create_path(path)
        with gzip.open(path, 'rb') as f_in:
            with open(bin_file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        logger.info('finish to unzip')
        return bin_file_path


def get_parent_directory(file_path):
    '''get a path as string , return the path to directory contains this file'''
    p = Path(file_path)
    parent = p.parent
    return  str(parent)

# file reader


class Reader():
    '''
    read the content of binary file
    @pre: file is it the following structure :32unit - data length
                                              data_length - data itself
    '''

    def __init__(self, bytes_file):

        self.path = bytes_file

    def read_file(self):
        '''
        generator function yield every time the next massage in the bytes file
        :return: stream of bytes represnt User or Snapshot
        '''

        with open(self.path, 'rb') as bf:
            data = bf.read(4)   # extract data_length
            logger.info('read 4 bytes')
            i = 1
            while data:
                num_of_bytes = struct.unpack('I', data)
                data = bf.read(num_of_bytes[0])     #extract data itself
                logger.info(f'read the next 4 bytes, the {i} iteration ')
                yield data
                data = bf.read(4)
                i += 1



###########################################
#
# logger section
#
###########################################

def create_logger(file_name):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # disable all third part library loggers
    disabled_modules= ['pika',' requests','flask','sqlalcemy']
    for m in disabled_modules:
        l = logging.getLogger(m)
        l.setLevel(logging.CRITICAL)
    fh = logging.FileHandler(file_name, mode='w')
    ch = logging.StreamHandler()
    # set logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # set handlers level
    fh.setLevel(logging.DEBUG)
    ch.setLevel(logging.ERROR)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger