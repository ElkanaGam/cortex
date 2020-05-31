# Cortex Project<br/>
The Advance System Design course final project

> Welcome to the cortex package.<br/> Cortex allow yow to capture your minds into `snapshots` objects, upload them, analayze them and visualize them!

## Table of Contents
- [description](#description)
- [Installation](#installation)
- [Usage](#Usage)
- [Configuration](#configuration)
- [Contact](#contact)

---
## Description
The cortex project is composed from three parts: The clinet - the part responseable to upload your data, the logic part: contains the server which  getting the data and delivering it to the parsers in microservise architecture and the storing system, and the third part is  user interface which includ gui interfae via a website and the api servise.

## Installation

> note:
Due to unfortunately circumsances cortex is not avialable with `Docker image` for the project.<br/> This will be fix at the next version. Therefore, follow the next step, to instal the package.

first clone the project from github:
```
git clone https://github.com/ElkanaGam/cortex.git
```
Then, in your shell:

```shell
$cd cortex
$./install.sh
$source .env/bin/activate
````
The project is ready to be run.

## usage 
Cortex can be used as a complete system, or alternatively you use it as python package, and take separates parts of it.<br/>
To run it as a complete system run the `run-pipline.sh` command. This supposed to install and run  all the needed part of the system: message-queue and database, and run the servers. After running this command, simply prepare your data file and run the `client`:
For example, from python shell, with the argument `path` is the path to the data:
``` python 
>>>from cortex.client import upload_sample
>>>upload_sample(host ='127.0.0.11, port = 8000, path =path)
```
Then you can browse to '127.0.0.1:8080' to view results.

All cortex modules can be run as cli , so you can also run this command from the shell:
```bash
$python -m cortex.client upload_sample -h 127.0.0.1 -p 8000 sample.mind
```
### Usage as  a python library
Cortex provide six modules, `client.py` was described above. <br/>
The Server is flask-based server which can be invoked from interpeter or shell.The server accept the data from the client and publish it. Therefore, beside host and port he server accept third argument: if it s invoked from command line this argument is the name of the message-queue, and this has to be a valid url to this queue. this url parsed by the `init_queue` function and it can be modified to handle your configuration for teh message queue . Running as function from interpetr allow to pass every object to publish the accepted data, as long as this object has `publish_data` function. In this case message_queue parameter has to be `None`.

```bash
python -m cortex.client run-server -h 127.0.0.1 -p 8000 raabitmq//127.0.0.1/5672 
```

```python 
>>>from cortex.server import run_server
>>>class my_publisher:
        __init__(self):
            ...
        def publish_data(self, data):
              print(data)
>>> p = my_publisher()
>>>run_server(host='127.0.0.1', port = 8000, p, message_queue = None)
```
The Parsers part is responsble to parse the data.To run the parser, one can run it using the `parse` command (from shell, or interpeter) which accept the parser name and source of data:
```bash
$python -m cortex.parsers parse 'pose' data 
```
This manner of invocation print the results of parsing.
The `Parsers.py` also provide service usage while consuming the data published by the server. Every parser that want to handle data has to register to the mesage-queue, this pricess will be described at the configuratin part.<br/>In this case the parsed dadta will be send farword to  database .Use `run-parser` command, which can only invoked from cli, and get the parser name, and mesagfe_queue url as parameters. In this case the data will be parsed and will be delivere again to the queue to registered db. If one intersred in multy invocation of all the parsers it can be done through the `run-all` command:
```bash
$python -m cortex.parsers run-parser 'color-image' 'rabbitmq//127.0.0.01:5672'
$python -m cortex.parsers run-all
```
The Saver is responsible to store the data. It expose the Saver class whisch accept database url and provid  the `save` command to store specific data:
```pytohn
>>>from cortec.saver import Saver
>>>s = Saver(db_url)
>>>data = {'name':'alice', 'user_id':12....}
>>>s.save('color_image',data)
```
The saver.py can be also used as service via command line, while accepting the db_url as cli argument:
```bash
$python -m cortex.saver run-saver 'postgres//127.0.0.1:5432'
```
To consume and view the data of the cortex system it provides two ways: REST-ful api server(defaultly listening at port 5000) , and a gui server to visualize the data (defaultly listening at port 8080).<br/>
The api expose the next points:
```
GET /users
GET /users/user_id
GET /users/user_id/snapshots
GET /users/user_id/snapshots/snapshot_id
GET /users/user_id/snapshots/snapshot_id/name
GET /users/user_id/snapshots/snapshot_id/name/data
```
Those api end-points used to consume snapshots history acording to user id, and snapshots id, for example:
```bash
$curl 127.0.0.1:5000/users/42/snapshots/3/pose
{
  "POSE": [
    {
      "rot_w": 0.952683103962489,
      "rot_x": -0.302622501147349,
      "rot_y": 0.0249845873195754,
      "rot_z": 0.0137947678556597,
      "time": "Wed, 04 Dec 2019 10:08:07 GMT",
      "trans_x": -0.0569029822945595,
      "trans_y": 0.0913627371191978,
      "trans_z": -0.145408257842064
    }
  ]
}

```
## Configuration

Coretx try to  allow to you flexiblity as much as it can. Those configuration can be made in under `projectu_utils\utils.py` file.
1. Adding another parser: you can add your costumaized function to parse the data. it even can be  your object. you parser has to handle json data (it is how the data deliverd in the queue), and all you need to do is to put your code under the cortex pacakge, and in `utils.py`, in the parsers_module variable, add your python cide name to the kist. that it. the collect function will collect your functions or nmethods.
```python 
>>>parsers_module = ['parsers_list', 'your_inoviative_parser']
```
2. Logs files directory, silent mode. and queue_message routing keys and excahnges, can be all controled and be modifie in the `utils.py`
in the apropriate variables
```python
# program constants
IMAGE_DIR = './static/images'
UPLOADS_NUM = inf
logger  = logging.getLogger(__name__)
SERVER_EXCHANGE = 'data_exchange'
SERVER_ROUTING_KEY = 'data'
USERS_RT_KEY = 'users'
SILENT_MODE = True
parsers_modules = ['parser_list']
```
3. Client issues:
the cliend demand a parser object to parse the raw data. this object has to be with `serialize(data, type='snapshot'), desrialize_data(data, type='snapshot')` method. This object is *not* exposed and has to be hard-coded in the client.py. the default protocol that suppotred by the server  is currently protobuf and all data is converted to this protocol via those parsers object.<br/>
Another elemnt that can be control is the UPLOADS_NUM - limit the numbers of uploaded snapshots, again in the `utils.py` file.

## Contact
Elkana1234@gmail.com. 

##
Enjoy :)

