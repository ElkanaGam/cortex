import sys
from project_utils.imagehandler import ImageHandler as Handler
import json
import logging

logger = logging.getLogger(__name__)

def log_function(parser):
    '''wrap parser to pass its details to logger'''
    def wrapper(*args, **kwargs):
        logger.info(f'In {parser.__name__}')
        return parser(*args, **kwargs)

    return wrapper


@log_function
def pose_parser(data):
    '''parse the pose data and return it as json '''
    data = json.loads(data)
    cols = ['user_id', 'datetime']+['trans_' + c for c in ['x', 'y', 'z']] + ['rot_' + c for c in ['x', 'y',
                                                                                 'z', 'w']]
    vals = [data[c] for c in cols]
    json_data = dict(zip(cols, vals))
    return json_data


@log_function
def color_image_parser(data):
    '''save the the color img '''
    data = json.loads(data)
    cols = ['user_id', 'datetime'] + ['img_size', 'color_img_path']
    vals = [data[c] for c in cols]
    json_data = dict(zip(cols, vals))
    # saving the image
    path = json_data['color_img_path']
    datetime = json_data['datetime']
    size = json_data['img_size']
    handler = Handler(path)
    row_data = handler.load_binary_color(datetime)
    img_path = handler.save_color_img(datetime,size, row_data)
    json_data['color_img_path'] = img_path
    json_data['color_img_width'] = size[0]
    json_data['color_img_height'] = size[1]
    return json_data

@log_function
def depth_image_parser(data):
    print('in parser')
    data = json.loads(data)
    cols = ['user_id', 'datetime']+['d_img_size', 'depth_img_path']
    vals = [data[c] for c in cols]
    json_data = dict(zip(cols, vals))
    path = json_data['depth_img_path']
    datetime = json_data['datetime']
    size = json_data['d_img_size']
    handler = Handler(path)
    row_data = handler.load_binary_depth(datetime,size)
    img_path = handler.save_depth_img(datetime, size, row_data)
    print(f'in depth {img_path}')
    json_data['depth_img_width'] = size[0]
    json_data['depth_img_height'] = size[1]
    json_data['depth_img_path'] = img_path

    return json_data


@log_function
def feelings_parser(data):
    data = json.loads(data)
    cols = ['user_id', 'datetime'] + ['hunger', 'thirst','exhaustion', 'happiness']
    vals = [data[c] for c in cols]
    json_data = dict(zip(cols, vals))
    return json_data