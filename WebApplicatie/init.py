from flask import Flask, render_template, request, url_for, redirect, session, g, flash, blueprints, jsonify
import pymysql, re, redis, gc, datetime
from pymysql import escape_string as escape
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
from flask_wtf import Form

from wtforms import PasswordField, validators, HiddenField, StringField
from wtforms import TextAreaField, BooleanField
from wtforms.validators import EqualTo, Optional, data_required
from wtforms.validators import Length, Email

store = RedisStore(redis.StrictRedis())

app = Flask(__name__, static_url_path='/static')
app.config.update(
    SESSION_COOKIE_NAME='DSS',
    SESSION_KEY_BITS=128
)

KVSessionExtension(store, app)

# @app.before_request
# def db_connect():
#     g.db_conn = pymysql.connect(host='213.233.237.7',
#                                  user='domotica',
#                                  password='SecretPass :O :O :O',
#                                  db='domotica_db',
#                                  charset='utf8',
#                                  port=3306)
#     global cur
#     cur = g.db_conn.cursor()

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/bewoner/')
def bewoner():
    return render_template("bewoner.html")

@app.route('/meldkamer/')
def meldkamer():
    return render_template("meldkamer.html")

@app.route('/admin/')
def admin():
    return render_template("admin.html")

if __name__ == '__main__':
    app.secret_key = '*87gas6&*(73()fa98Nla&$62Nv%#{az' #Secret key for sessions | This key HAS TO BE CHANGED IN THE FINAL VERSION (and not being published on GitHub)
    app.run(debug=True)