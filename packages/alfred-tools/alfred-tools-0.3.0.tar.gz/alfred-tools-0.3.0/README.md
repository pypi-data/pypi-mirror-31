[![PyPI version](https://badge.fury.io/py/alfred-tools.svg)](https://badge.fury.io/py/alfred-tools)
# ALFRED

Tool to automate projects in DjangoFramework

### To Do List

- [ ] Generate automatic CRUD {Views, Models, Forms, Admin, Html}
- [x] Generate new secret key
- [ ] Update automatic new secretkey
- [ ] Making and Run automatic Test

Any suggestions? Send a pull request to this list! 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
 - Python 3.x
 - Django 
 
```

### Installing

A step by step series of examples that tell you have to get a development env running

#### Unix, Linux or OSX
Say what the step will be

```
pip install alfred-tools

```

Later add in you INSTALLED_APPS

```
'alfred-tools',

```


### Using

####Generate new SECRET_KEY for django projects
```
python3 manage.py newsecretkey

```


####Generator Crud (Code in Views.py and templates files blank) for django apps

Check that your app is in the apps module for example:
```
'apps.appname'

```
Later using the command + appname
```
python3 manage.py generatorcrud appname

```
and write the name of your model for example test:
```
Input New Model Crud: test

```
 
## Versioning
See more in [CHANGELOG](CHANGELOG.md)


 
## Authors
[@kevinzelada.cl](https://github.com/kevinzeladacl/)
 
See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License
[MIT](seed/LICENSE)