import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image
import struct
import io
# the structure of the static is : every user has his own directory
# which name as his id. the static  binary content are saved by the server to
# this directory in the following structure : <datetime>_<image_type>
# and the static themselves are saved to in that directory by parsers
# at the following structure: <datetime>_<image_type>.jpg
#
# for example: for user_id: 12,datetime 1001,
# /root - running program location
#    /12
#       /1001_color
#       /1001_depth
#       /1001_color.jpg
#       /1001_depth.jpg




class ImageHandler:

    def __init__(self, path, suffix = None):
        '''

        :param path: path to the dirctory of current user
        :param suffix:
        '''
        self.path = Path(path)
        self.suffix = suffix
        self.preffix = '../gui/static/images'

    def load_binary_color(self,datetime):
        '''
            return binary content of file
        :param path: the path to file
        :return:
        '''
        path = self.path / (str(datetime)+'_color')
        with open(path, 'rb') as f:
            bin_data = f.read()
        return bin_data

    def load_binary_depth(self, datetime, img_size):
        length = img_size[0]*img_size[1]
        path = self.path / (str(datetime) + '_depth')
        with open (path, 'rb') as f:
            bin_data = f.read()
        data = struct.unpack(f'{length}f',bin_data)
        return list(data)

    def save_binary_color(self,datetime,  img_size, img_data ):
        image_path = Path(self.path) /  (str(datetime) + '_color')  # image storage location
        with open (image_path, 'wb') as f:
            f.write(img_data)
        return str(self.path)

    def save_binary_depth(self, datetime,  img_size, img_data):
        image_path = Path(self.path) / (str(datetime) + '_depth')
        buf = struct.pack(f'{len(img_data)}f', *img_data)
        with open (image_path, 'wb') as f:
            f.write(buf)
        return str(self.path)


    def save_depth_img(self, datetime,  img_size, img_data):
        image_path = self.path / (str(datetime) +'_depth'+'.jpg')  # image storage location
        points = np.asarray(img_data)
        array_data = points.reshape(img_size)
        plt.imsave(image_path,array_data, cmap='hot')
        return str(image_path)

    def save_color_img(self, datetime,  img_size, img_data):
        image_path = self.path / (str(datetime) + '_color'+ '.jpg')  # image storage location
        im = Image.frombytes('RGB', img_size, img_data, 'raw')
        im.save(image_path)
        return str(image_path)


