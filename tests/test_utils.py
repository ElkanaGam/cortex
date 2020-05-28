import pytest
import struct
from pathlib import Path

from project_utils import utils


@pytest.fixture()
def bin_file(tmp_path):
    p = Path(tmp_path) / "bin_file"
    with open (p, 'wb') as f:
        massage = b'hello world'
        length = len(massage)
        d = struct.pack('I', length)
        d = bytearray(d)
        d += massage
        f.write(d)
        massage = b'goodbye world'
        length = len(massage)
        d = struct.pack('I', length)
        d = bytearray(d)
        d += massage
        f.write(d)
    return  p


def test_reader(bin_file):
    reader = utils.Reader(bin_file)
    reader_gen = reader.read_file()
    with pytest.raises(StopIteration):
        data = next(reader_gen).decode('utf8')
        assert data == 'hello world'
        data = next(reader_gen).decode('utf8')
        assert data == 'goodbye world'
        data = next(reader_gen)


def test_get_parent_directory():
    p = Path.cwd() / 'temp_test'
    print(str(p))
    p.mkdir(exist_ok=True)
    file_name = p / 'file.txt'
    with open (file_name, 'w') as f:
        f.write('hello')
    str_path  = str(file_name)
    assert utils.get_parent_directory(str_path) == str(p)
