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
#     g.db_conn = pymysql.connect(host='host@host.com',
#                                  user='username',
#                                  password='password',
#                                  db='databasename',
#                                  charset='utf8',
#                                  port=3306)
#     global cur
#     cur = g.db_conn.cursor()

@app.route('/')
def main():
    return render_template("home.html")

if __name__ == '__main__':
    app.secret_key = '*87gas6&*(73()fa98Nla&$62Nv%#{az' #Secret key for sessions
    app.run(debug=True)