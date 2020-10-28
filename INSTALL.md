# <img src="omw/static/omw-logo.svg" width="48" height="48" alt="OMW logo" /> Installing Open Multilingual Wordnet

* [Installing the software](#Installing-the-software)
* [Creating the database](#Creating-the-database)
* [Running in Debug Mode](#Running-in-Debug-Mode)

## Installing the software

To setup OMW, start by cloning the repository and changing to its directory:

```bash
~$ git clone https://github.com/globalwordnet/OMW.git
~$ cd OMW/
~/OMW$
```

This application utilizes older versions of some packages, as specified in [`requirements.txt`](requirements.txt).
For that reason, we suggest the creation of isolated Python environments using [virtualenv](https://virtualenv.pypa.io) to install such versions.

If you don't already have virtualenv, install it by running the command:
```
~/OMW$ pip install virtualenv
```

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

## Creating the database

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

After installing the software and creating the database, you can run the OMW web app on your local machine with `run.py`:

``` bash
(py3env) ~/OMW$ python run.py
```

If successful, you should be able to view the OMW by visiting http://0.0.0.0:5000/


