from telebot import types
from bot import bot  # Импортируем объект бота
from db import users_db


def enter_name(message, our_db_table):
    our_db_table['name'] = message.text
    for db in users_db.find():
        if db['chat_id'] == message.chat.id:
            users_db.update_one(db, {"$set": our_db_table})
            break
    if not our_db_table['age']:
        bot.send_message(message.chat.id, 'Введите ваш возраст')
    else:
        main_menu(message)


def enter_age(message, our_db_table):
    forbidden_list = our_db_table['forbidden_ages'].split(", ")
    if message.text.isdigit() and message.text not in forbidden_list:
        our_db_table['age'] = message.text
        our_db_table['forbidden_ages'] += (", " + message.text)
        for db in users_db.find():
            if db['chat_id'] == message.chat.id:
                users_db.update_one(db, {"$set": our_db_table})
                break
    else:
        if message.text == 'Отмена':
            age = our_db_table['forbidden_ages'].split(", ")[-1]
            users_db.update({ 'age': our_db_table['age'] }, { "$set": { "age": age}})

        if not our_db_table['age'] and message.text != "Отмена":
            bot.send_message(message.chat.id, 'Вы ввели невалидный возраст, попробуйте снова:')
            return

    if not our_db_table['gender']:
        enter_gender(message)
    else:
        main_menu(message)


def enter_gender(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row('Мужской', 'Женский')
    if message.text == 'Мужской' or message.text == 'Женский':
        db_table = {}
        fill_place = {}
        for x in users_db.find():
            if x['chat_id'] == message.chat.id:
                db_table = x
                fill_place = db_table.copy()
                fill_place['gender'] = message.text
        users_db.update_one(db_table, { "$set": fill_place })
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "Укажите ваш пол:", reply_markup=keyboard)


def main_menu(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row('Изменить имя')
    keyboard.row('Изменить возраст')
    keyboard.row('Изменить пол')
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=keyboard)


def change_name(message, our_db_table):
    keyboard = types.ReplyKeyboardRemove()
    our_db = our_db_table.copy()
    our_db['name'] = None
    users_db.update(our_db_table, { "$set": our_db })
    bot.send_message(message.chat.id, 'Введите имя:', reply_markup=keyboard)


def change_age(message, our_db_table):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Отмена")
    our_db = our_db_table.copy()
    our_db['age'] = None
    users_db.update(our_db_table, { "$set": our_db })
    bot.send_message(message.chat.id, 'Введите ваш возраст:', reply_markup=keyboard)


def change_gender(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row('Сменить')
    keyboard.row('Отменить')
    bot.send_message(message.chat.id, "Хотите изменить пол?", reply_markup=keyboard)

def conformation(gender):
    if gender == "Мужчина":
        users_db.update({ "gender": gender }, { "$set": { "gender": "Женщина" } })
    else:
        users_db.update({ "gender": gender }, { "$set": { "gender": "Мужчина" } })

"""
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    if call.message:
        if call.data == "change_name":
            change_name(call.message, our_db_table)
        elif call.data == "change_age":
            change_age(call.message, our_db_table)
        elif call.data == "change_gender":
            change_gender(call.message)
        elif call.data == "confirm":
            conformation(our_db_table['gender'])
            main_menu(call.message)
        elif call.data == "cancel":
            if not our_db_table['age']:
                age = our_db_table['forbidden_ages'].split(", ")[-1]
                users_db.update({'age': our_db_table['age']}, {"$set": {"age": age}})
            main_menu(call.message)"""


@bot.message_handler(commands=['who'])
def delete(message):
    for db in users_db.find():
        if db['chat_id'] == message.chat.id:
            bot.send_message(message.chat.id, 'Имя: {}, возраст: {}, пол: {}'.format(db['name'], db['age'], db['gender']))
            break

@bot.message_handler(commands=['del'])
def delete(message):
    users_db.delete_many({})


@bot.message_handler(commands=['start'])
# Выполняется, когда пользователь нажимает на start
def send_welcome(message):
    keyboard = types.ReplyKeyboardRemove()
    if not users_db.find_one({ "chat_id": message.chat.id }):
        users_db.insert_one(
            {
                "chat_id": message.chat.id,
                "name": None,
                "age": None,
                "gender": None,
                "forbidden_ages": "",
            }
        )
        bot.send_message(message.chat.id, 'Введите имя:', reply_markup=keyboard)
    else:
        main_menu(message)


@bot.message_handler(content_types=['text'])
def catcher_of_text(message):
    our_db_table = {}
    for db in users_db.find():
        if db['chat_id'] == message.chat.id:
            our_db_table = db
            break
    if not our_db_table['name']:
        enter_name(message, our_db_table)
    elif not our_db_table['age']:
        enter_age(message, our_db_table)
    elif not our_db_table['gender']:
        enter_gender(message)
    elif message.text == "Изменить имя":
        change_name(message, our_db_table)
    elif message.text == "Изменить возраст":
        change_age(message, our_db_table)
    elif message.text == "Изменить пол":
        change_gender(message)
    elif message.text == "Отмена":
        main_menu(message)
    elif message.text == "Сменить":
        conformation(our_db_table['gender'])



if __name__ == '__main__':
    bot.polling(none_stop=True)
