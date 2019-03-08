# -*- coding: utf-8 -*-

# For debugging only! Do not run this on a production server!

from omw import app

if __name__ == '__main__':
   app.run(host='127.0.0.1', port=5000, debug=True)
