TARGET=/var/www/OMW
SERVER=localhost

mkdir -p "${TARGET}"
if [ -d "${TARGET}/venv" ]
then
    source ${TARGET}/venv/bin/activate
    pip install -r requirements.txt
else   
    python3 -m venv "${TARGET}/venv"
    source ${TARGET}/venv/bin/activate
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
fi
   

#cp -r venv "${TARGET}"

#cp -r omw "${TARGET}"

### Create .wsgi
cat >"${TARGET}/omw.wsgi" <<EOF
### file created by OMW/deploy.sh

import sys, os

# activate_this = '${TARGET}/venv/bin/activate_this.py'
# with open(activate_this) as file_:
#     exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, os.path.dirname(__file__))
from omw import app as application

EOF


### Create apache config file
cat >"/etc/apache2/sites-available/OMW.conf" <<EOF

<VirtualHost *>
    ServerName ${SERVER}

    WSGIDaemonProcess omw threads=5 python-home=${TARGET}/venv/ 

    WSGIScriptAlias /omw ${TARGET}/omw.wsgi 

    <Directory ${TARGET} >
        WSGIProcessGroup yourapplication
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
</VirtualHost>
EOF

sudo a2ensite OMW

sudo service apache2 restart
