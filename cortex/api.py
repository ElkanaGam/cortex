import os
import click
from pathlib import Path
import sys
import shutil
from flask import Flask , request, jsonify, render_template, send_file, url_for, send_from_directory
from saver import DataBase, schema



# cols names for every topic
topic_cols = {'pose': ['time','trans_x', 'trans_y', 'trans_z',
                       'rot_x', 'rot_y', 'rot_w', 'rot_z'],
              'color_image': ['time','color_img_width', 'color_img_path', 'color_img_height'],
              'depth_image': ['time','depth_img_path', 'depth_img_width', 'depth_img_height'],
              'feelings': ['time','hunger', 'thirst', 'exhaustion', 'happiness']}

all_cols = []
for k in list(topic_cols.keys()):
    all_cols += topic_cols[k][1:]
all_cols.append('time')



app = Flask(__name__)
global db

def pack(ret, data_name):
    j = {data_name:[]}
    for row in ret:
        d = dict(row)
        t = {}
        for k, v in d.items():
            t[k] = v
        j[data_name].append(t)
    return j

@app.route('/', methods=['GET'])
def hello():
    print('in server')
    return 'welcome to api server'

@app.route('/users', methods=['GET'])
def users():
    ret = app.config['db'].get_cols('users',['user_id','name'])
    return jsonify(pack(ret,'USERS'))

@app.route('/users/<user_id>')
def user_id_data(user_id):
    ret = app.config['db'].get_row('users','user_id',user_id)
    return jsonify(pack(ret,'USER_DATA'))


@app.route('/users/<user_id>/snapshots')
def user_id_snapshots(user_id ):
    ret = app.config['db'].get_data('snapshots',user_id,['id','time'])
    print('sna')
    return jsonify(pack(ret,'SNAPSHOTS'))


@app.route('/users/<user_id>/snapshots/<s_id>')
def avialable_topics(user_id, s_id):
    available = {'pose':True, 'color_image':True, 'depth_image':True, 'feelings':True}
    ret = app.config['db'].get_data('snapshots',user_id,all_cols,s_id)
    for r in ret:
        d = dict(r)
        for k, v in d.items():
            if d[k] == None:
                print(k)
                print('topics = ',list(topic_cols.keys()))
                for topic in list(topic_cols.keys()):
                    print(topic_cols[topic])
                    if k in topic_cols[topic]:
                        available[topic] = False
    print(available)
    data = {s_id:{'available':[k for k, _ in available.items() if available[k]],'time':d['time']}}
    return jsonify(data)


@app.route('/users/<user_id>/snapshots/<s_id>/<name>')
def topic_result(user_id,s_id,name):
    if name not in ['color_image', 'depth_image']:
        cols = topic_cols[name]
        ret = app.config['db'].get_data('snapshots',user_id,cols,s_id=s_id)
        return pack(ret,name.upper())
    else:
        cols = topic_cols[name]
        ret = app.config['db'].get_data('snapshots',user_id,cols,s_id=s_id)
        for r in ret:
            d = dict(r)
            data= {}
            data['depth_img_height'] = d['depth_img_height']
            data['depth_img_width'] = d['depth_img_width']
            data['url_for_img'] = f'/users/{user_id}/snapshots/{s_id}/{name}/data'
            data['time'] = d['time']
            return pack([data], name.upper())

@app.route('/users/<user_id>/snapshots/<s_id>/<name>/data')
def images_data(user_id,s_id,name):
    cols = topic_cols[name]
    ret = app.config['db'].get_data('snapshots', user_id, cols, s_id=s_id)
    topic = name.rsplit('_',1)[0]+'_img_path'
    src_img_path = pack(ret,name)[name][0][topic][11:]

    print(Path(src_img_path))
    p = src_img_path.replace(os.sep, '/')
    return send_from_directory('static', filename = p)




@click.option('--host','-h', default='127.0.0.1',
              help='host of api server')
@click.option('--port', '-p', default=5000, help='port of api server')
@click.option('--database','-d',default=schema)
@click.command()
def run_api_server(host = '127.0.0.1', port=5000, database=schema):
    app.config['db'] = DataBase(database)
    app.run(host=host, port=port, debug=True)

@click.group()
def main():
    pass

main.add_command(run_api_server)

if __name__ == '__main__':
    main()

