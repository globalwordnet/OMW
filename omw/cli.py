
import click

from omw import app
from omw.omw_sql import init_omw_db, init_admin_db

@app.cli.command(name='init-admin-db')
def init_admin_db_command():
    init_admin_db()
    click.echo('Admin database initialized')

@app.cli.command(name='init-omw-db')
def init_omw_db_command():
    init_omw_db()
    click.echo('OMW database initialized')
