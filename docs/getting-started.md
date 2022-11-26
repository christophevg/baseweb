# Getting Started

Baseweb is hosted on PyPi, so...

```bash
$ pip install baseweb
```

## Minimal Survival Commands

To actually run baseweb you need additionally a web server, like gunicorn, optionally with async support, e.g. using eventlet.

```bash
$ pip install https://github.com/benoitc/gunicorn/archive/ff58e0c6da83d5520916bc4cc109a529258d76e1.zip
$ pip install eventlet
```

Now you can start a stock baseweb using:

```bash
$ gunicorn -k eventlet -w 1 baseweb.web:server
```

And you will get...

![baseweb stock](baseweb-stock.png)

Which is an empty baseweb, serving a (non-existing) application from your current folder (in my case called Workspace).

## A little more...

From a cloned instance of the baseweb repository, simply issue `make` to get a running instance of the demo app that is part of the repository: 

```bash
$ make
*** building a virtual environment
Running virtualenv with interpreter /Library/Frameworks/Python.framework/Versions/3.5/bin/python3
Using base prefix '/Library/Frameworks/Python.framework/Versions/3.5'
New python executable in /Users/xtof/Workspace/baseweb/venv/bin/python3
Also creating executable in /Users/xtof/Workspace/baseweb/venv/bin/python
Installing setuptools, pip, wheel...
done.
*** setting up requirements
*** starting the web container
[2020-02-05 00:12:11 +0100] [51457] [INFO] Starting gunicorn 20.0.4
[2020-02-05 00:12:11 +0100] [51457] [INFO] Listening at: http://127.0.0.1:8000 (51457)
[2020-02-05 00:12:11 +0100] [51457] [INFO] Using worker: eventlet
[2020-02-05 00:12:11 +0100] [51461] [INFO] Booting worker with pid: 51461
[2020-02-05 00:12:11 +0100] [baseweb.config] [51461] [DEBUG] baseAdmin config = {'app': {'author': 'Christophe VG', 'root': '/Users/xtof/Workspace/baseweb', 'name': 'demo', 'description': 'A demo app for baseweb'}}
[2020-02-05 00:12:11 +0100] [baseweb.web] [51461] [INFO] baseweb web server is ready...
[2020-02-05 00:12:11 +0100] [baseweb.interface] [51461] [INFO] registered component index.js from /Users/xtof/Workspace/baseweb/demo/pages/index
```

Now visit [http://localhost:8000](http://localhost:8000), enter your name and press a few buttons to see the demo app in action, presenting some of the standard features offered by baseweb.

![baseweb demo](baseweb-demo.png)

Finally inspect the `demo/` folder to see how to build the application or read on for a step by step walk through of [building your first baseweb app](building-your-first-baseweb-app.md).
