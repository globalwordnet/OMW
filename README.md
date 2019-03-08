# OMW

Code for the Open Multilingual Wordnet ---
read in wordnets, validate them, and search them.

Currently running here: http://compling.hss.ntu.edu.sg/iliomw


DB Schema:
https://docs.google.com/spreadsheets/d/1-FFnIaw0_6aJ6a--wfooNnGQlVpfl-hTxof8mWmX0P8/edit?usp=sharing
(may be out of date)


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
~/OMW$ virtualenv -p python3 env
~/OMW$ source env/bin/activate
(env) ~/OMW$
```

Now install the dependencies and download [WordNet](https://wordnet.princeton.edu/) for [NLTK](http://www.nltk.org/):

```bash
(env) ~/OMW$ pip install -r requirements.txt
(env) ~/OMW$ python -c 'import nltk; nltk.download("wordnet")'
```

With the dependencies satisfied, you are ready to create the databases for running the OMW interface:

``` bash
(env) ~/OMW$ bash create-db.sh
```

The above command will prompt for an email and password for the admin database, and allow you to create additional users.
At this point you may want to inspect and edit the created `config.py` file to ensure it is correct for your installation.
When done, you are ready to run the web app.

## Running in Debug Mode

You can run the OMW web app on your local machine with `run.py`:

``` bash
(env) ~/OMW$ python run.py
```

If successful, you should be able to view the OMW by visiting http://0.0.0.0:5000/

## Deploying

The included `omw.wsgi` file can help you get started with deploying to an Apache2 server with `mod_wsgi`.
See the [Flask documentation](http://flask.pocoo.org/docs/1.0/deploying/mod_wsgi/) for more information.
