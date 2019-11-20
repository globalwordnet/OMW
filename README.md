# <img src="omw/static/omw-logo.svg" width="48" height="48" alt="OMW logo" /> The Open Multilingual Wordnet

Code for the Open Multilingual Wordnet ---
read in wordnets, validate them, and search them.

Currently running here: http://compling.hss.ntu.edu.sg/iliomw


DB Schema:
https://docs.google.com/spreadsheets/d/1-FFnIaw0_6aJ6a--wfooNnGQlVpfl-hTxof8mWmX0P8/edit?usp=sharing
(may be out of date) or on github: https://github.com/globalwordnet/schemas with docs: https://globalwordnet.github.io/schemas/


## Setup

To setup OMW, start by cloning the repository and changing to its directory:

```bash
~$ git clone https://github.com/globalwordnet/OMW.git
~$ cd OMW/
~/OMW$
```

This application utilizes older versions of some packages, as specified in [`requirements.txt`](requirements.txt).
For that reason, we suggest the creation of isolated Python environments using [virtualenv](https://virtualenv.pypa.io) to install such versions.
See [here](https://virtualenv.pypa.io/en/latest/installation/) for instructions on installing virtualenv itself if you don't already have it.
Now create and activate new virtual environment:

```bash
~/OMW$ virtualenv -p python3 py3env
~/OMW$ source py3env/bin/activate
(py3env) ~/OMW$
```

Note that the virtual environment resides in a subdirectory called `py3env` (you may choose a different name).
Now install the dependencies and download [WordNet](https://wordnet.princeton.edu/) for [NLTK](http://www.nltk.org/):

```bash
(py3env) ~/OMW$ pip install -r requirements.txt
(py3env) ~/OMW$ python -c 'import nltk; nltk.download("wordnet")'
```

With the dependencies satisfied, you are ready to create the databases for running the OMW interface:

``` bash
(py3env) ~/OMW$ bash create-db.sh
```

The above command will prompt for an email and password for the admin database, and allow you to create additional users.
At this point you may want to inspect and edit the created `config.py` file to ensure it is correct for your installation.
It should have settings like the following:

``` python
UPLOAD_FOLDER = '.../omw/public-uploads'
RESOURCE_FOLDER = '.../omw/resources'
SECRET_KEY = # the output of something like `python3 -c 'import os; print(os.urandom(24))'`
OMWDB = '.../omw/db/omw.db'
ADMINDB = '.../omw/db/admin.db'
ILI_DTD = '.../omw/db/WN-LMF.dtd'
```

The paths in `config.py` do not need to be under the `omw/` subdirectory, so you may adjust them as needed, but you may need to then move the files that were created by `create-db.sh`.

Finally, you may wish to generate lists of examples for each relation, but this step is optional. The `scripts/get-examples.py` script can do this for a given database and language code. You may wish to re-run the command after adding new wordnets. The results should be written to the `RESOURCE_FOLDER` location with the filename `relation-examples.$LG.tsv` where `$LG` is the language code. For example:

``` bash
(py3env) ~/OMW$ python3 scripts/get-examples.py omw/db/omw.db en -n100 > omw/resources/relation-examples.en.tsv
```

The `-n100` option means to output (up to) 100 examples for every relation.

When done, you are ready to run the web app.

## Running in Debug Mode

You can run the OMW web app on your local machine with `run.py`:

``` bash
(py3env) ~/OMW$ python run.py
```

If successful, you should be able to view the OMW by visiting http://0.0.0.0:5000/

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
