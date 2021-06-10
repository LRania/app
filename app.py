# -*- coding: UTF-8 -*-
"""
hello_flask: First Python-Flask webapp
"""
from flask import Flask, jsonify, make_response, request
from redis import Redis, RedisError
from flask_sqlalchemy import SQLAlchemy
#from flask_script import Manager
#from flask_migrate import Migrate, MigrateCommand
from sqlalchemy.exc import OperationalError
import psycopg2



import os
import socket
import time
import json
import sys

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)


app = Flask(__name__)
#https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/#flask_sqlalchemy.SQLAlchemy.engine
#postgresql:/URI format
#postgresql://scott:tiger@localhost/mydatabase

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://objectrocket:orkb123@10.144.180.121:5432/ordb'
db = SQLAlchemy()

timeout = time.time() + 100 * 5

@app.route("/getEnv")
def getEnv():
    db_name = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    pwd = os.environ['POSTGRES_PASSWORD']
    return db_name

    
class User(db.Model):
    __tablename__ = 'info_table'
 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String())
    age = db.Column(db.Integer())
 
    def __init__(self, name,age):
        self.name = name
        self.age = age
 
    def __repr__(self):
        return '<User %r>' % self.username

def add_User(conn, table_name):
    page = "insert "
    surname = "Leonard"
    givename = "Rania"
    age = int("58")
    error = 0
    try:
        cur = conn.cursor()
        #INSERT INTO table_name(column1, column2, …) VALUES (value1, value2, …);

        
        sql = "INSERT INTO %s (surname, givename, age) VALUES (%s, %s, %i);"% (table_name, surname, givename,age)
        page += sql
        cur.execute("""INSERT INTO %s (surname, givename, age) VALUES (%s, %s, %i); """, (table_name, surname, givename,age))
        conn.commit()
    except Exception as ex:
        page += repr(ex)
        error = 2
    return page, error
    
    
@app.route('/create_db', methods=['GET', 'POST'])
def create_db():
    page ="Param: "
    server = "127.0.0.0"
    port= "5032"
    db_name = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    pwd = os.environ['POSTGRES_PASSWORD']
    conn = None
    table_name = "customer_table"
    
    for text in request.form:
        if (text == 'IP'):
            server = request.form['IP']
            page += server
        if (text == "Port"):
            port = request.form['Port']
            page += port
        if (text == "Table"):
            table_name = request.form['Table']
            page += table_name

    config = "postgresql://" +user+ ":" +pwd + "@" + server + ":" + port + "/" + db_name
    page = config 
    cnx = "host={} dbname= {} user={} password={}".format(server, db_name, user, pwd)
    #connection = "host=%s dbname=%s user=%s password=%s"% (HOST, DATABASE,USER, PASSWORD))
    
    try:
        #conn = psycopg2.connect(server, user, pwd, port, db_name)
        conn = psycopg2.connect(cnx)
        page += "--- connect OK "
        cur = conn.cursor()

        sql = "CREATE TABLE IF NOT EXISTS {} (surname TEXT PRIMARY KEY, givename TEXT, age INTEGER);".format(table_name)
        cur.execute(sql)
        page += "--- create table OK : " + sql
        conn.commit()
        txt, rcode  = add_User(conn, table_name)
        if (rcode == 0):
            page += "--- add_user OK " + txt
        else:
            page += "--- add_user ERROR " + txt
        
        cur.execute("DROP TABLE IF EXISTS {};".format(table_name))
        conn.commit()
        page += "--- drop table OK "
        conn.close()
        page += "--- close OK "
    except psycopg2.Error as error:
        print(error.pgerror)
        page += error.pgerror
        page += "== psycopg2.Error =="
        return page
    except Exception as ex:
        message = ex.__class__.__name__
        exc_type, value, traceback = sys.exc_info()
        page += exc_type.__name__
        page += repr(ex)
        return page

    return page
    

@app.route('/test_db')
def test_db():
    db_name = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    pwd = os.environ['POSTGRES_PASSWORD']
    page = "test_db - "
    config = app.config['SQLALCHEMY_DATABASE_URI']
    page += config
    
    try:
        db.create_all()
        page += "create - "
        db.session.commit()
        page += "commit - "
        user = User.query.first()
        if not user:
            u = User(name='Mudasir', surname='Younas')
            db.session.add(u)
            db.session.commit()
        user = User.query.first()
        return "User '{} {}' is from database".format(user.name, user.surname)
    except:
        return page



@app.route("/contact")
def contact():
    mail = "leonard.rania@fr.ibm.com"
    tel = "01 23 45 67 89"
    return "Mail: {} --- Tel: {}".format(mail, tel)

@app.route("/healthz/ready")
def readiness():
    time.sleep(1)
    return "OK"

@app.route("/healthz/live", methods=['GET'])
def liveness():
    headers = {'Content-Type': 'text/plain'}
    delay = time.time()
    if (delay < timeout):
        return "OK", 200, {'Content-Type': 'text/plain'}
    else:
        return "timeout", 408, {'Content-Type': 'text/plain'}

@app.route("/")
def hello():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>" \
           "<b>Visits:</b> {visits}"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=visits)


if __name__ == '__main__':  # Script executed directly?
    print("Hello World! Built with a Docker file.")
    app.run(host="0.0.0.0", port=5000, debug=True,use_reloader=True)  # Launch built-in web server and run this Flask webapp
