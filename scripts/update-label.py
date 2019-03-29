#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from omw import app, g, updateLabels, connect_omw

with app.app_context():
    g.omw = connect_omw()
    updateLabels()
    g.omw.close()
