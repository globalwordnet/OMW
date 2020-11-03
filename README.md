# <img src="omw/static/omw-logo.svg" width="48" height="48" alt="OMW logo" /> The Open Multilingual Wordnet

Code for the Open Multilingual Wordnet ---
read in wordnets, validate them, and search them.

Currently running here: https://compling.hss.ntu.edu.sg/iliomw


DB Schema:
https://docs.google.com/spreadsheets/d/1-FFnIaw0_6aJ6a--wfooNnGQlVpfl-hTxof8mWmX0P8/edit?usp=sharing
(may be out of date) or on github: https://github.com/globalwordnet/schemas with docs: https://globalwordnet.github.io/schemas/

## Contents
* [Installation and Database setup](#Installation-and-Database-setup)
* [Deploying](#Deploying)
* [Local Testing](#Local-Testing)
* [Contribute](#Contribute)

## Installation and Database setup

To setup OMW, [follow these instructions](https://github.com/globalwordnet/OMW/blob/develop/INSTALL.md).

## Deploying

The included [`omw.wsgi`](omw.wsgi) file can help you get started with deploying to an Apache2 server with `mod_wsgi`.
See the [Flask documentation](http://flask.pocoo.org/docs/1.0/deploying/mod_wsgi/) for more information.

If you are running a virtual environment (which is recommended) for a deployment with Apache2 and `mod_wsgi`, note the following:

* You must use the same version of Python that `mod_wsgi` is compiled against (see [here](https://modwsgi.readthedocs.io/en/develop/user-guides/virtual-environments.html#virtual-environment-and-python-version)).
* If your need to use `sudo` to create and install packages to the virtual environment, running `sudo pip install -r omw/requirements.txt` with the environment active will **not** work; instead, use `sudo py3env/bin/pip install -r omw/requirements.txt` (adjusting paths as needed for your setup).
* As described [here](https://modwsgi.readthedocs.io/en/develop/user-guides/virtual-environments.html#daemon-mode-multiple-applications), you may need to activate the virtual environment from the WSGI script. See [`omw.wsgi`](omw.wsgi) for an example.

## Local Testing

You can load a wordnet from the command line:

``` bash
(py3env) ~/OMW$  PYTHONPATH=.  python scripts/validate-wn.py /home/bond/work/omw/jpn/jpn.xml 
```

Note that you may still have to add the project, and possibly the language, from the web interface (under CILI: Project and Source Administration or Language Administration).

## Contribute

Join our mission, [contribute to the Open Multilingual Wordnet](https://github.com/globalwordnet/OMW/blob/develop/CONTRIBUTING.md).