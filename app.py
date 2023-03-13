import os
import flask
from flask import Flask, request
import requests
import json
import socket
import string
from string import Template
import random
import pymongo
from pymongo import MongoClient

import time

app = Flask(__name__)
data = {}


def get_collection():
    client = MongoClient(data['address'],
                         username=data['userName'],
                         password=data['password'],
                         authSource="admin")
    db = client.shortener_db
    return db.shortener_collection


@app.route('/', methods=['POST'])
def url_shortener():
    long_url = request.form['u']
    print(long_url)
    can_insert = False
    short_url = ''
    shortener_collection = get_collection()
    while not can_insert:
        short_url = 'shortener-service:' + str(data['port']) + '/'
        short_url = short_url + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        db_instance = shortener_collection.find_one({"short_url": short_url})
        if db_instance == None:
            can_insert = True
    expire_time = time.time() + data['exp']
    instance = {
        "short_url": short_url,
        "long_url": long_url,
        "expire_time": expire_time
    }
    shortener_collection.insert_one(instance)
    return short_url


@app.route('/<short_url>')
def redirect(short_url):
    short_url = 'shortener-service:' + str(data['port']) + '/' + short_url
    shortener_collection = get_collection()
    db_instance = shortener_collection.find_one({"short_url": short_url})
    if db_instance == None:
        return 'Not Found'
    elif db_instance.get('expire_time') < time.time():
        return 'Not Found'
    else:
        return flask.redirect(db_instance.get('long_url'))


if __name__ == '__main__':
    if os.path.exists('./config.json'):
        with open('./config.json') as conf:
            data = json.load(conf)
            data['userName'] = os.getenv('SHORTENER_USER_NAME')
            data['password'] = os.getenv('SHORTENER_PASSWORD')
    else:
        data["port"] = 8080
        data["exp"] = 100
        data["address"] = "mongodb://localhost:27017"
        data["userName"] = "database"
        data["password"] = "urlShortenerDB"
    app.run(host="0.0.0.0", debug=True, port=data['port'])
