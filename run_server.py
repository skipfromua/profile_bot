import flask
from flask import request
from flask_admin import Admin
from telebot import types
from werkzeug.utils import redirect

from config import *
from bot_handlers import bot
from db import users_db
import os

server = flask.Flask(__name__)
admin = Admin(server)

@server.route('/admin/' , methods=['POST'])
def sender():
    for x in users_db.find():
        if request.form['text_area']:
            bot.send_message(x['chat_id'], request.form['text_area'])
    return redirect('/admin')


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([types.Update.de_json(flask.request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route('/', methods=["GET"])
def index():
    bot.remove_webhook()
    bot.set_webhook(url="https://pacific-thicket-10824.herokuapp.com/{}".format(TOKEN))
    return "Hello from Heroku!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))