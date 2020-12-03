
# Import functions and objects the microservice needs.
# - Flask is the top-level application. You implement the application by adding methods to it.
# - Response enables creating well-formed HTTP/REST responses.
# - requests enables accessing the elements of an incoming HTTP/REST request.
#
import process_got_json
# Setup and use the simple, common Python logging framework. Send log messages to the console.
# The application should get the log level out of the context. We will change later.
#

import os
import sys
import inspect
import copy

cwd = os.getcwd()
sys.path.append(cwd)

import logging
from datetime import datetime


from flask import Flask, Response
from flask import request
import flask

import resources.Characters as C
import resources.Actors as A

application = Flask(__name__)

# This function performs a basic health check. We will flesh this out.
@application.route("/health", methods=["GET"])
def health_check():

    rsp_data = { "status": "healthy", "time": str(datetime.now()) }
    rsp_str = process_got_json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="application/json")
    return rsp


@application.route("/characters", methods=["GET", "POST"])
def get_characters():

    args = request.args
    res = C.get_characters_by_query(args)

    rsp = Response(process_got_json.dumps(res), status=200, content_type="application/json")
    return rsp


@application.route("/characters/<ch_id>", methods=["GET"])
def get_character_by_id(ch_id):

    res = C.get_character_by_id(ch_id)

    rsp = Response(process_got_json.dumps(res), status=200, content_type="application/json")
    return rsp


@application.route("/characters/<ch_id>/<r_kind>", methods=["GET"])
def get_related_characters(ch_id, r_kind):

    res = C.get_related_characters(ch_id, r_kind)

    rsp = Response(process_got_json.dumps(res), status=200, content_type="application/json")
    return rsp


@application.route("/actors/<actor_id>", methods=["GET"])
def get_actor_by_id(actor_id):

    res = A.get_actor_by_id(actor_id)

    rsp = Response(process_got_json.dumps(res), status=200, content_type="application/json")
    return rsp


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.

    application.debug = True
    #application.before_request(do_something_before)
    #application.after_request(do_something_after)
    application.run(host='0.0.0.0', port=8025)