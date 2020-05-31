# parser imports
import sys
#import parser_list
import importlib
from inspect import getmembers , isclass, isfunction
import threading
import click
# message queue import
from project_utils.consumer import Consumer
from project_utils.publisher import Publisher
from project_utils import  utils

# Queue names 
SRC_EX = utils.SERVER_EXCHANGE
SRC_RT_KEY = utils.SERVER_ROUTING_KEY
DEST_EX = 'database'
logger = utils.create_logger('logs/parsers.log')
silent = utils.SILENT_MODE
#silent = True
module_names = utils.parsers_modules



def init_queue(message_queue_scheme):
    '''Instantiate message queue in host according to shceme'''
    name, host, port = message_queue_scheme.split(':')
    if name != 'rabbitmq':
        print('This Message Queue is not suppotred')
        raise Exception
        logger.error('message queueu url is not supported')
    else:
        host = host[2:]
        consumer = Consumer(SRC_EX, host=host)
        logger.info(f'instantiate consumer at{host}')
        return consumer
def _collect_modules(m_list):
    for m in m_list:
        importlib.import_module(m)
        logger.info(f'dynamicly imported {m} ')

def _collect_parsers_as_func(module_names, p_list):
    '''collect al the parsers funcion from a given module'''
    logger.info('collect all function')
    for m in module_names:
        for name, obj in getmembers(sys.modules[m]) :
            if 'parser' in name and isfunction(obj):
                p_list[name.rsplit('_',1)[0]] = obj  
    

def _collect_parsers_as_class(module_names, p_list):
    '''collect all the parsres function of object from a given module'''
    logger.info('collect all object methods as parsers')
    for m in module_names:
        cls = [c for _, c in getmembers(sys.modules[m]) if isclass(c) ]
        for c in cls:
            for name, obj in getmembers(c):
                if 'parser' in name and isfunction(obj):
                    instance = c()
                    parsers_list[name.rsplit('_',1)[0]] = getattr(instance, name)




@click.command()
@click.argument('parser_name')
@click.argument('source')
def parse(parser_name, source):
    '''Get parser name and raw data source , parse it, and print it'''
    try:
        # parse from file case
        if type(source) is str:
            logger.info(f'Parse data with {parser_name} and print it')
            with open(source, 'r') as f:
                data = f.read()
            print(parsers_list[parser_name](data))
        # parse row data case
        else:
            data = source
            logger.info(f'Parse data with {parser_name} and return it')
            return parsers_list[parser_name](data)
    except Exception as e:
        logger.exception(f'error while parsing from {source}')




@click.command()
@click.argument('parser_name')
@click.argument('message_queue_url')
def run_parser(parser_name, message_queue_url):
    '''Parse data with according to the parser_name and publish to queue '''
    logger.info(f'start consume and parse from {message_queue_url} with {parser_name}')
    available_parsers = [name for name, p in parsers_list.items()]
    if parser_name not in available_parsers:
        print("This parser is not available."
              " you can try:" )
        # show available parsers
        for p in available_parsers:
            print(p)
        
        logger.info(f'{parser_name} doesnt exist')
        return
    c = init_queue(message_queue_url)
    c.create_connection()
    c.bind_connection(SRC_RT_KEY)
    parser = (parsers_list[parser_name])
    def callback(ch, method, properties, body):
        logger.info(f'in {parser_name} callback')
        p = Publisher(DEST_EX)
        data = parser(body)
        name = parser_name
        if not silent:
            print(data)
        if name != 'user':
            data['parser_name'] = name
        # publish to database as excahnge and routing key is spesified by parser name
        p.publish_data(data, name)
    c.consume_data(callback)



@click.command()
def run_all(to_print=True):
    '''Parse data with all avialable parsers and publish to queue '''
    threads = []
    for p_name in parsers_list.keys():
        c = Consumer(SRC_EX)
        c.create_connection()
        c.bind_connection(SRC_RT_KEY)
        p = get_parser(parsers_list, p_name)
        thread = threading.Thread(target=consume_and_publish, args=(c, p, p_name))
        threads.append(thread)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

def get_parser(p_list, name):
    return p_list[name]

def consume_and_publish(consumer,parser, name, to_print=True):
    print(f'start consuming with {name} ')
    def callback(ch, method, properties, body):
        publisher = Publisher(DEST_EX)
        data = parser(body)
        if to_print:
            print(data)
        if name != 'user':
            data['parser_name'] = name
        # publish to database as excahnge and routing key is spesified by parser name
        publisher.publish_data(data, name)
    consumer.consume_data(callback)


@click.group()
def main():
    pass


main.add_command(parse)
main.add_command(run_all)
main.add_command(run_parser)

if __name__ == '__main__':
    parsers_list = {}
    # start collectin all the parsers
    _collect_modules(module_names)
    _collect_parsers_as_func(module_names, parsers_list)
    _collect_parsers_as_class(module_names,parsers_list)
    avialable = [p for p in parsers_list.keys()]

    main()