
# OMW Scripts

Many of the scripts in this directory are called when first
initializing the database, while others may be separately. For scripts
that open the OMW database, you'll need to set `PYTHONPATH` when
calling them. For instance, to add a user:

``` bash
$ PYTHONPATH=. python3 scripts/add-user.py
```
