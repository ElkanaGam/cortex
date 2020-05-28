import click
import json
import sys
import datetime
import threading
import logging
from project_utils.consumer import Consumer
import project_utils.utils as utils
from sqlalchemy import *

schema = 'postgres://postgres:elkana1@127.0.0.1/db'

def _parse_scheme(scheme,avialable = ['postgres']):
    name = schema.split('://')[0]
    if name not in avialable:
        raise Exception('Only postgresql in supported currently ')
    else:
        return schema


class DataBase :
    '''
    Create and manage the database for the cortex system
        the system has 2 tables:
        Users: every row contains different user details
        Snapshots: every row contains different snapshot data, and
        unique by the user_id and time stamp_row
    '''

    def __init__(self, schema, ):
        '''
        create conection to database with the scheme supplied
        :param schema: database url to be connected
        :param log: log
        '''
        self.engine = create_engine(schema, echo=False)
        self.metadata = MetaData(bind=self.engine)
        self.log = logging.getLogger(__name__)

    def create_users_table(self):
        '''
        cretate the table to hold all users details
        :return: None
        '''
        t = Table('users', self.metadata,
                 Column('id', Integer, primary_key=True),
                 Column('user_id', Integer),
                 Column('name', String),
                 Column('birthdate', Integer),
                 Column('gender', Integer))
        self.metadata.create_all(self.engine)
        self.log.error("users table created")

    def create_snapshot_table(self):
        '''
        create the table to hold all snapshots
        :return: None
        '''
        t = Table('snapshots', self.metadata,
                  Column('id', Integer, primary_key=True),
                  Column('user_id', Integer),
                  Column('time', DateTime(timezone=True)),
                  Column('trans_x', Float),
                  Column('trans_y', Float),
                  Column('trans_z', Float),
                  Column('rot_x', Float),
                  Column('rot_y', Float),
                  Column('rot_w', Float),
                  Column('rot_z',Float),
                  Column('color_img_width',Integer),
                  Column('color_img_height',Integer),
                  Column('color_img_path', String),
                  Column('depth_img_width', Integer),
                  Column('depth_img_height', Integer),
                  Column('depth_img_path', String),
                  Column('hunger', Float),
                  Column('thirst', Float),
                  Column('exhaustion', Float),
                  Column('happiness', Float))
        self.metadata.create_all(self.engine)
        self.log.error("snapshot table created")


    def _create_dami_table(self):
        '''
        create simple table. for testing only
        :return: None
        '''
        t = Table('dami_snapshots', self.metadata,
                  Column('id', Integer, primary_key=True),
                  Column('user_id', Integer),
                  Column('time', Integer),
                  Column('trans_x', Float),
                  Column('trans_y', Float),extend_existing=True)
        self.metadata.create_all(self.engine)

    def insert_user_data(self,data):
        table = self.metadata.tables['users']
        u_id = data['user_id']
        check_exixt = select([table]).where(table.c['user_id'] == u_id)
        conn = self.engine.connect()
        res = conn.execute(check_exixt)
        if res.rowcount > 0:
            self.log.info(f' user {u_id} already exist')   
            return  
        query = table.insert(data)
        self.log.info(f'insert new user {u_id} data')
        conn = self.engine.connect()
        conn.execute(query)

    def insert_topic_data(self, topic_data, filters):
        '''
        update topic data for specific timestamp.
        :param topic_data: the data to be insert to table
        :param filters: cols in table to be update
        :return: None
        '''
        timestamp = datetime.datetime.fromtimestamp(topic_data['datetime']/1000)
        user_id = topic_data['user_id']
        # fetch snapshot table
        self.metadata.reflect(bind=self.engine)
        table = self.metadata.tables['snapshots']
        values_dict = {k:v for k, v in topic_data.items() if k in filters}
        values_dict['user_id'] = user_id
        values_dict['time'] = timestamp
        # checking if this timestamp already exist for this user
        query = select([table]).where(and_(
                                    table.c.time==timestamp,
                                    table.c.user_id == user_id))
        conn = self.engine.connect()
        res = conn.execute(query)

        if res.rowcount > 0:        # row already exist for timpstamp
            self.log.info(f'record at {timestamp} already  exist')
            #  execute update query
            updt = table.update().where(and_(
                                    table.c.time==timestamp,
                                    table.c.user_id == user_id)).values(values_dict)
            conn.execute(updt)
            self.log.info('update record')
        else:                       # first insertion for timstamp
            self.log.info(f'not exist record for time {timestamp}')
            # execute insert query
            ins = table.insert().values(values_dict)
            self.log.info('update record')
            conn.execute(ins)


    def remove_tables(self):
        '''
        remove all table from self.metadata
        :return: None
        '''
        self.metadata.reflect(bind=self.engine)
        for table in reversed(self.metadata.sorted_tables):
            self.log.error(f'dropping {table.name}')

            self.metadata.drop_all(bind=self.engine, tables=[table])
            self.metadata.clear()


    def get_data(self,table_name,user_id,cols_names,s_id=None):
        '''
        retrun data for specific user and spesific row,
        if timestamp is specified
        :param user_id: the user_id for the user own the desired data
        :param timestamp: the timestamp for the desired data
        :return: ResultProxy contain all the rows in the result of the query
        '''
        self.metadata.reflect(bind=self.engine)
        self.log.info(f'fetching datafrom {table_name} {user_id} id')
        table = self.metadata.tables[table_name]
        connection = self.engine.connect()
        if s_id is not None:
            # return all the table
            query = select([table.c[n] for n in cols_names]).where(and_(
                                    table.c['user_id'] == user_id,
                                    table.c['id'] == s_id))
        else:
            query = select([table.c[n] for n in cols_names]).where(
                                    table.c.user_id == user_id)
        return connection.execute(query)

    def get_row(self,table_name,col_name,value):
        self.log.info(f'fetching data from {table_name}, value = {value}')
        self.metadata.reflect(bind=self.engine)
        table = self.metadata.tables[table_name]
        connection = self.engine.connect()
        query = select([table]).where(table.c[col_name] == value)
        ret = connection.execute(query)
        return ret

    def get_cols(self, t_name, cols_names):
        self.log.info(f'fetching data from {t_name}')
        self.metadata.reflect(bind=self.engine)
        table = self.metadata.tables[t_name]
        connection = self.engine.connect()
        query = select([table.c[n] for n in cols_names])
        ret = connection.execute(query)
        return ret



class Saver:

    def __init__(self, database_url):
        self.url = _parse_scheme(database_url)
        self.db = DataBase(self.url)
        self.log = logging.getLogger(__name__)

    # this function is called from python shell
    def save(self,topic_name, data):
        topic_cols = {'pose':['trans_x','trans_y','trans_z',
                              'rot_x','rot_y','rot_w','rot_z'],
                      'color_image':['color_img_width','color_img_path','color_img_height'],
                      'depth_image':['depth_img_path', 'depth_img_width', 'depth_img_height'],
                      'feelings':['hunger','thirst','exhaustion','happiness']}

        self.db.insert_topic_data(data, topic_cols[topic_name])

    def get_data(self, user_id, timestamp=None):
        return self.db.get_data(user_id, timestamp)

    def save_user_data(self, to_print = True):
        def callback(ch, method, properties, body):
            data = json.loads(body)
            if to_print:
                print(data)
            self.log.info('consume user data')
            self.db.insert_user_data(data)

        c = Consumer(utils.SERVER_EXCHANGE)
        c.create_connection()
        c.bind_connection(utils.USERS_RT_KEY)
        c.consume_data(callback)

logger = utils.create_logger('logs/saver.log')

@click.command()
def clear():
    schema = 'postgres://postgres:elkana1@127.0.0.1/db'
    db = DataBase(schema)
    logger.info('clearing all data base tables ')
    db.remove_tables()


# this function is invoked from cli
@click.command()
@click.argument('name')
@click.argument('path')
@click.option('--database', '-d', default='postgresql://127.0.0.1:5432')
def save(name, path, database):
    with open (path , 'rb') as f:
        s = Saver(database)
        data = json.load(f)
        s.save(name, data)


@click.command()
@click.argument('database',default='postgresql://127.0.0.1:5432')
def run_saver(database, to_clear=False):
    # clear previous data in data base
    if to_clear:
        clear()
    the_saver = Saver(database)
    the_saver.db.create_snapshot_table()
    the_saver.db.create_users_table()
    threads = []
    user_trd = threading.Thread(target = the_saver.save_user_data, args=())
    threads.append(user_trd)
    #the_saver.save_user_data()
    parsers = ['pose', 'color_image', 'depth_image', 'feelings']
    def _save():
        def callback(ch, method, properties,body):
            data = json.loads(body)
            t = data['datetime']
            print(f'data at {t} arrived')
            name = data['parser_name']
            logger.info(f'save data from {name}')
            the_saver.save(name, data)
        c = Consumer('database')
        logger.info('consuming at saver')
        c.create_connection()
        for p in parsers:
            c.bind_connection(p)
            print(f'Waiting .... [{p}] ')
        c.consume_data(callback)
    data_trd = threading.Thread(target=_save, args = ())
    threads.append(data_trd)

    for t in threads:
        t.start()
    for t in threads:
        t.join()





@click.group()
def cli():
    pass

cli.add_command(save)
cli.add_command(run_saver)
cli.add_command(clear)

if __name__ == '__main__':
    cli()