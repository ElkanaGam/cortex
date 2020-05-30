# Cortex Project<br/>
The Advance System Design course final project

> Welcome to the cortex package.<br/> Cortex allow yow to capture your minds, upload them, analayze them and visualize them!

## Table of Contents
- [description](#description)
- [Installation](#installation)
- [Usage](#Usage)
- [Configuration](#configuration)
- [Team](#team)

---
## Description
The cortex project is composed from three parts: The clinet - the part responseable to upload your data, the logic part: contains the server which  getting the data and delivering it to the parsers in microservise architecture and the storing system, and the third part is  user interface which includ gui interfae via a website and the api servise.

## Installation

> note:
Due to unfortuntly circumsances cortex is not avialable with `Docker` image for the project.<br/> This will be fix at the next version. Therefor, follow the next step, to instal the package.

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
Cortex can be used as a coplete system or alternatively you can take separates part of it.<br/>
To run it as a coplete system run the `run-pipline.sh` command. This supposed to  install and run  all the needed part of the system: message-queue and database, and run the servers. After running this command, simply prepare your data file and run the `client`:
from python shell, with the argument `path` is the path to the data:
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
Cortex provide six modules, client.py was described above. <br/>
The Server is flask-based server which can be invoked from interpeter or shell. Beside host and port he server accept third argument: if it s invoked from command line this argument is the name of the message-queue, and this has to be a valid url to this queue.this url parsed by the `init_queue` function . Running as function from interpetr allow to pass every object to publish the accepted data, as long as this object has `publish_data` function. In this case message_queue parameter has to be `None`.

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

```
