from flask import Flask, render_template, Response , request, redirect, url_for
from pathlib import Path
from datetime import datetime as dt
import os
import click
from sqlalchemy import *
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import ticker


schema = 'postgres://postgres:elkana1@127.0.0.1/db'

##
#
# SERVER SECTION
#
##

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    num = get_num_of_users()
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if not is_user_exist(int(user_id)):
            feedback = f'user {user_id} does not exist'
            return render_template('./index.html', feedback = feedback)
        return redirect(f'/{user_id}')
        
    return render_template('./index.html', num = num)
    

@app.route('/<user_id>') 
def user_page(user_id):
    '''this page show last suploaded snapshot'''
    items = get_last_snapshots(user_id)
    username=get_user_name(user_id)
    items['color_img_path'] = items['color_img_path']
    items['depth_img_path'] = items['depth_img_path']
    return render_template('./user_home_page.html', user_id=user_id, username=username, items=items)


@app.route('/<user_id>/options', methods=['GET', 'POST'])
def user_options(user_id):
    '''this page show the optinal data to view'''
    if request.method == 'POST':
        data_type = request.form['data_type']
        num_of_snapshots= request.form.get('num')
        
        return redirect(f'/{user_id}/data?data_type={data_type}&num={num_of_snapshots}')
        
    max_snap = get_num_of_snapshots()
    return render_template('./option.html', user_id=user_id, max_snap=max_snap)

@app.route('/<user_id>/data')
def user_data(user_id):
    data_type = request.args.get('data_type')
    num = request.args.get('num')
    username = get_user_name(user_id)
    
    # get the data from database
    data_table = get_topic_by_time_range(data_type,num, user_id)
    items = tranform_table(data_table)
    src = ''
    # felling case
    if data_type == 'feelings':
        name = get_feelings_plot(data_table,num)
        src = url_for('static', filename=name)
    return render_template(f'./{data_type}_data.html',  items=items, username=username, num=num, user_id=user_id, src=src)

@click.command()
@click.option('--port', '-p',default=8080)
@click.option('--host', '-h', default='127.0.0.1')
@click.argument('url)
def run_server():
    app.run(host='127.0.0.1', port = 8080,url , debug=True)


##
#
# RETRIEVE FROM DB SECTION
#
##
engine = create_engine(schema, echo=False)
metadata = MetaData(bind=engine)



def get_num_of_users():
    metadata.reflect(bind=engine)
    table = metadata.tables['users']
    query = select([table])
    conn = engine.connect()
    res = conn.execute(query)
    return (res.rowcount)
    
def get_num_of_snapshots():
    metadata.reflect(bind=engine)
    table = metadata.tables['snapshots']
    query = select([table])
    conn = engine.connect()
    res = conn.execute(query)
    return (res.rowcount)


def get_last_snapshots(user_id):
    metadata.reflect(bind=engine)
    table = metadata.tables['snapshots']
    query = select([table]).where(table.c['user_id'] == user_id).order_by(desc(
        table.c['id'])).limit(1)
    conn = engine.connect()
    res = conn.execute(query)
    for row in res:
        return dict(row)




def get_topic_by_time_range(topic_name,snap_num,user_id):
    metadata.reflect(bind=engine)
    table = metadata.tables['snapshots']
    cols = {'feelings':['exhaustion','happiness','thirst','hunger','time'],
            'color':['time', 'color_img_path'],
            'depth':['time', 'depth_img_path'],
            'position':['time','trans_x','trans_y','trans_z']}
    topic_cols = cols[topic_name]
    above_to = get_id_of_ith_snapshot(int(snap_num), user_id)
    query = select([table.c[col] for col in topic_cols]).where(and_(table.c['user_id']==user_id,
                                       table.c['id']>above_to))
    conn = engine.connect()
    res = conn.execute(query)
    # consrtuct table of the results
    data_table = {c:[] for c in topic_cols}
    for row in res:
        table_r = dict(row)
        for k, v in table_r.items():
            data_table[k].append(v)
    #for k, v in data_table.items():
    #    print(k)
    #   pretty_print(v)
    #    print()
    return data_table


def get_id_of_ith_snapshot(i, user_id):
    last = get_last_snapshots(user_id)
    last_id = last['id']
    first = last_id-i
    return max(first, 0)


def pretty_print(l):
    for i in l:
        print('< ', i)

def get_user_name(user_id):
    metadata.reflect(bind=engine)
    table = metadata.tables['users']
    query = select([table.c['name']]).where(table.c['user_id']==user_id)
    conn = engine.connect()
    res = conn.execute(query)
    for r in res:
        name =  dict(r)['name']
        print(name)
        return name


def is_user_exist(user_id):
    '''return if user is registerd'''
    metadata.reflect(bind=engine)
    table = metadata.tables['users']
    query = select([table]).where(table.c['user_id'] == user_id)
    conn = engine.connect()
    res = conn.execute(query)
    return  res.rowcount > 0



def tranform_table(table_dict):
    '''{k1:[...], k2[###]} --> [{k1:.,k2:#},...]'''
    l = []
    for i in range(len(table_dict['time'])):
        elem = {}
        for k in list(table_dict.keys()):
            if k == 'color_img_path' or k== 'depth_img_path':
                table_dict[k][i] = table_dict[k][i][6:].replace(os.sep, '/')
            elem[k]=table_dict[k][i]
        l.append(elem)
    return l

def get_feelings_plot(data_table, fig_name):
    
    fig, axes = plt.subplots(ncols=2, nrows=2, figsize = (10, 8))
    names = ['hunger', 'happiness', 'exhaustion', 'thirst']
    colors = dict(zip(names,['#1C4048','#28D3E0','#FF0909','#6B11AF']))
    max_bin = min(12,len(data_table['time']))
    
    for i, ax in enumerate(axes.flatten()):
        x = data_table['time']
        x_time = [str(t)[11:22] for t in x]
        y = data_table[names[i]]   
        ax.set_title(f'{names[i]} by time')
        ax.xaxis.grid(color='w',linestyle='-.')
        ax.yaxis.grid(color='w',linestyle='-.') 
        ax.set_facecolor('#EAE6E8')
        ax.set_ylim([-1,1])
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=max_bin))
        ax.tick_params(axis='x', which='major', labelsize=8)
        for l in ax.get_xticklabels():
            l.set_rotation(90)
        ax.plot(x_time, y, color = colors[names[i]])
    plt.tight_layout()
    path = (f'./static/images/feelings_plot/{fig_name}_feelings.jpg')
    plt.savefig(path,bbox_inches = "tight")
    return f'images/feelings_plot/{fig_name}_feelings.jpg'


@click.group()
def main():
    pass

main.add_command('run_server')
if __name__ == '__main__':
    main()
    
