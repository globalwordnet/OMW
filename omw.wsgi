
import sys, os

# Use the following to activate a virtual environment
# python_home = '/path/to/virtual/environment'  # adjust as needed
# activate_this = python_home + '/bin/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))  # Python 2
# exec(open(activate_this).read(), dict(__file__=activate_this))  # Python 3

# adjust as needed for your server; consider using an absolute path
sys.path.insert(1, os.path.dirname(__file__))

from omw import app as application
