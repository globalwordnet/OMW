# OMW

Code for the Open Multilingual Wordnet ---
read in wordnets, validate them, and search them

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
When the command has completed, you are ready to run the web app.

## Running in Debug Mode

You can run the OMW web app on your local machine in debug mode with `flask run`:

``` bash
(env) ~/OMW/omw$ FLASK_APP=. flask run
```

**Note:** Currently you must run the above command from the `omw/` subdirectory.

If successful, you should be able to view the OMW by visiting http://0.0.0.0:5000/

