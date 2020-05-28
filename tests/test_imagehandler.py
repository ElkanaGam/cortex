from pathlib import Path
from project_utils.imagehandler import ImageHandler
from PIL import  Image
from numpy.random import uniform
from read_bytes import Reader
from project_utils.dataparser import Parser
from project_utils import cortex_pb2, utils

BINARY_PATH = '/home/user/Documents/cortex/client/color_img_for_testing'

def generate_depth_points():
    r = Reader('/home/user/Documents/cortex/client/sample.mind')
    g = r.read_file()
    garbage = next(g)   # skip user data
    data = next(g)      # extract first snapshot data
    p = Parser(cortex_pb2, cortex_pb2)
    depth_data = p.deserialize(data).depth_image.data
    width = p.deserialize(data).depth_image.width
    height = p.deserialize(data).depth_image.height
    data = utils._convert_to_list(depth_data)
    return data, (width, height)




def genetrate_points(size):
    l = uniform(low = -1, high =1, size = (size, ))
    return l

def rm_tree(pth):
    pth = Path(pth)
    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()

def user_directory():
    '''
    to be decorated by @pytest.fixture
    :param tmp_path:
    :return:
    '''
    c = Path.cwd() / '12'
    c.mkdir(exist_ok=True)
    # # copy the data file
    # src = Path(BINARY_PATH)
    # dest = c / '1001_color'
    # shutil.copy(str(src), str(dest))
    return str(c)


def test_save_binary_color():
    with open(BINARY_PATH, 'rb') as f:    # path to binary data
        data = f.read()
    h = ImageHandler(user_directory())
    new_path = h.save_binary_color(1001, (100, 100), data)
    assert new_path == str(Path(h.path) / '1001_color')  # assert the file was created
    with open(new_path, 'rb') as f:
        content = f.read()
    assert content == data  # assert hat this is the content
    assert Path(new_path).exists()

def test_save_color_img():
    h = ImageHandler(user_directory())
    data = h.load_binary_color(1001)
    p = h.save_color_img(1001, (1920, 1080), data)

    assert Path(p).exists()
    im = Image.open(p)
    # im.show()
    # rm_tree(user_directory())

def test_save_depth_binary():
    h = ImageHandler(user_directory())
    data, size = generate_depth_points()
    p = h.save_binary_depth(1001, size, data)
    assert Path(p).exists()
    load_data = h.load_binary_depth(1001, size)
    assert load_data == data

def test_save_depth_img():
    h = ImageHandler(user_directory())
    img_data = h.load_binary_depth(1001, (224, 172))
    p = h.save_depth_img(1001, (224, 172), img_data)
    assert Path(p).exists()
def test_clear():
    # rm_tree(user_directory())
    pass


