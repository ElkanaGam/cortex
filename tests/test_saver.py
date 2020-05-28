import json

import pytest
import saver
import click
from click.testing import CliRunner

runner = CliRunner()
@pytest.fixture
def create_data(tmp_path):
    data = {'user_id': 42,
            'time': 1001,
            'trans_x': 0.7,
            'trans_y': 0.71,
            'trans_z': 0.72,
            'rot_x': 0.73,
            'rot_y': 0.74,
            'rot_w': 0.75,
            'rot_z': 0.76,
            'color_img_width': 100,
            'color_img_path': 'color_path',
            'color_img_height': 200,
            'depth_img_path': 'depth_path',
            'depth_img_width': 150,
            'depth_img_height': 120,
            'hunger': 0.2,
            'thirst': 0.4,
            'exhaustion': 0.6,
            'happiness': -0.1}
    c = tmp_path /'topic.result'
    with open (c, 'w') as f:
        json.dump(data, f)
    return str(c)

def prepare_db():
    saver.clear()
    s = saver.DataBase(saver.schema)
    s.create_snapshot_table()

def test_save(create_data):
    prepare_db()

    r = runner.invoke(saver.save,['pose',create_data, '-d','postgresql://127.0.0.1:5432'])
    assert r.exit_code == 0
    r = runner.invoke(saver.save, ['feelings', create_data, '-d', 'postgresql://127.0.0.1:5432'])
    assert r.exit_code == 0


# @click.command()
# def test_save_from_shell():
#     s = saver.Saver(saver.schema)
#     # isert this command!!!
#     s.db.create_snapshot_table()
#     data = {'user_id':42,
#                   'time': 1001,
#                   'trans_x':0.7,
#                   'trans_y':0.71,
#                   'trans_z':0.72,
#                   'rot_x':0.73,
#                   'rot_y':0.74,
#                   'rot_w':0.75,
#                   'rot_z':0.76,
#                   'color_img_width':100,
#                   'color_img_path':'color_path',
#                   'color_img_height':200,
#                   'depth_img_path':'depth_path',
#                   'depth_img_width':150,
#                   'depth_img_height':120,
#                   'hunger':0.2,
#                   'thirst':0.4,
#                   'exhaustion':0.6,
#                   'happiness':-0.1}
#     topics = ['pose', 'color_image', 'depth_image', 'feelings']
#     for t in topics:
#         s.save(t,data)
#
#     for r in s.get_data(42):
#         d = dict(r)
#         for k, v in d.items():
#             print(f'{k} --->     {v}'  )
#
# if __name__ == '__main__':
#     test_save()

