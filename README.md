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
