# Getting Started

Baseweb is hosted on PyPi, so...

```bash
$ pip install baseweb
```

## Minimal Survival Commands

To actually run baseweb you need additionally an ASGI web server like gunicorn with uvicorn:

```bash
$ pip install gunicorn uvicorn
```

Now you can start a stock baseweb using:

```bash
$ gunicorn -w 1 -k uvicorn.workers.UvicornWorker "baseweb:server._asgi_app"
```

And when you visit [http://localhost:8000](http://localhost:8000) you will get...

![baseweb stock](baseweb-frame.png)

Which is an empty baseweb, serving a (non-existing) application from your current folder (in my case called Workspace). This is the baseweb frame in which your pages can be injected.

## A little more...

To quickly add a little more, clone the baseweb-demo repository and give that a spin...

```bash
% git clone https://github.com/christophevg/baseweb-demo
% cd baseweb-demo
% pip install -e .
% pip install gunicorn uvicorn
% gunicorn -w 1 -k uvicorn.workers.UvicornWorker "app:asgi_app"
```

Now visit [http://localhost:8000](http://localhost:8000) again, enter your name and press a few buttons to see the demo app in action, presenting some of the standard features offered by baseweb.

![baseweb demo](baseweb-demo.png)

Finally inspect the `baseweb-demo/` folder to see how to build the application or read on for a step by step walk through of [building your first baseweb app](building-your-first-baseweb-app.md).

> Pro-Tip: you can always clone/fork the `baseweb-demo` repository to start a new baseweb application ;-)
