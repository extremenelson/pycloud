# KVM-based Discoverable Cloudlet (KD-Cloudlet) 
# Copyright (c) 2015 Carnegie Mellon University.
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.
# 
# Released under a modified BSD license, please see license.txt for full terms.
# DM-0002138
# 
# KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
# MiniMongo
# Copyright (c) 2010-2014, Steve Lacy 
# All rights reserved. Released under BSD license.
# https://github.com/MiniMongo/minimongo/blob/master/LICENSE
# 
# Bootstrap
# Copyright (c) 2011-2015 Twitter, Inc.
# Released under the MIT License
# https://github.com/twbs/bootstrap/blob/master/LICENSE
# 
# jQuery JavaScript Library v1.11.0
# http://jquery.com/
# Includes Sizzle.js
# http://sizzlejs.com/
# Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
# Released under the MIT license
# http://jquery.org/license

import logging
import os.path

# Pylon imports.
from pylons import request, response
from pylons.controllers.util import abort
from paste import fileapp

# For serializing JSON data.
import json

# Controller to derive from.
from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.utils import timelog
from pycloud.pycloud.model import App

log = logging.getLogger(__name__)


################################################################################################################
# Class that handles Service VM related HTTP requests to a Cloudlet.
################################################################################################################
class AppPushController(BaseController):

    # Maps API URL words to actual functions in the controller.
    API_ACTIONS_MAP = {'': {'action': 'getList', 'reply_type': 'json'},
                       'get': {'action': 'getApp', 'reply_type': 'binary'}}

    ################################################################################################################
    # Called to get a list of apps available at the server.
    ################################################################################################################
    @asjson
    def GET_getList(self):
        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request for stored apps received.")

        os_name = request.params.get('osName', None)
        os_version = request.params.get('osVersion', None)
        tags = request.params.get('tags', None)

        print "OS Name: ", os_name
        print "OS Version: ", os_version
        print "Tags: ", tags

        query = {}

        if tags:
            # TODO: modify this to search not only in tags, but in service id as well.
            query['tags'] = {"$in": tags.split(',')}

        apps = App.find(query)

        # Send the response.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        timelog.TimeLog.writeToFile()
        return apps
        
    ################################################################################################################
    # Called to get an app from the server.
    ################################################################################################################
    def GET_getApp(self):
        app_id = request.params.get('appId', None)
        if not app_id:
            # If we didnt get a valid one, just return an error message.
            print "No app name to be retrieved was received."
            abort(400, '400 Bad Request - must provide app_id')
        
        print '\n*************************************************************************************************'    
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request to push app received.")

        app = App.by_id(app_id)
        if not app:
            print "No app found for specified id"
            abort(404, '404 Not Found - app with id "%s" was not found' % app_id)

        # Check that the APK file actually exists.
        file_exists = os.path.isfile(app.apk_file)
        if not file_exists:
            print "No APK found for app with specified id. Path: " + app.apk_file
            abort(404, '404 Not Found - APK for app with id "%s" was not found' % app_id)

        # Log that we are responding.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        timelog.TimeLog.writeToFile()                                

        # Create a FileApp to return the APK to download. This app will do the actually return execution;
        # this makes the current action a middleware for this app in WSGI definitions.
        # The content_disposition header allows the file to be downloaded properly and with its actual name.
        #fapp = fileapp.FileApp(app.apk_file, content_disposition='attachment; filename="' + app.file_name() + '"')
        #reply = fapp(request.environ, self.start_response)

        # Instead of returning the file by parts with FileApp, we will return it as a whole so that it can be encrypted.
        response.headers['Content-disposition'] = 'attachment; filename="' + app.file_name() + '"'
        response.headers['Content-type'] = 'application/vnd.android.package-archive'
        with open(app.apk_file, 'rb') as f:
            reply = f.read()

        # Send the response, serving the apk file back to the client.
        return reply
