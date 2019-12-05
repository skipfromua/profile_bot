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
        bot.send_message(message.chat.id, 'Вы ввели невалидный возраст, попробуйте снова:')
        if not our_db_table['age']:
            age = our_db_table['forbidden_ages'].split(", ")[-1]
            users_db.update({ 'age': our_db_table['age'] }, { "$set": { "age": age } })
            return

    if not our_db_table['gender']:
        enter_gender(message)
    else:
        main_menu(message)


def enter_gender(message):
    if message.text == 'Мужской' or message.text == 'Женский':
        users_db.update_one({ 'gender': None }, { "$set": { "gende": message.text } })
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row('Мужской', 'Женский')
    bot.send_message(message.chat.id, "Укажите ваш пол?", reply_markup=keyboard)


def main_menu(message):
    keyboard = types.ReplyKeyboardMarkup()
    change_name_button = types.InlineKeyboardButton(text="Изменить имя", callback_data="change_name")
    change_age_button = types.InlineKeyboardButton(text="Изменить возраст", callback_data="change_age")
    change_gender_button = types.InlineKeyboardButton(text="Изменить пол", callback_data="change_gender")
    keyboard.add(change_name_button)
    keyboard.add(change_age_button)
    keyboard.add(change_gender_button)
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=keyboard)


def change_name(message, our_db_table):
    our_db = our_db_table.copy()
    our_db['name'] = None
    users_db.update(our_db_table, { "$set": our_db })
    bot.send_message(message.chat.id, 'Введите имя:')


def change_age(message, our_db_table):
    keyboard = types.ReplyKeyboardMarkup()
    cancel_button = types.KeyboardButton(text="Отмена", callback_data="cancel")
    keyboard.add(cancel_button)
    our_db = our_db_table.copy()
    our_db['age'] = None
    users_db.update(our_db_table, { "$set": our_db })
    bot.send_message(message.chat.id, 'Введите ваш возраст:', reply_markup=keyboard)


def change_gender(message):
    keyboard = types.ReplyKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton(text="Сменить", callback_data="confirm")
    cancel_button = types.InlineKeyboardButton(text="Отмена", callback_data="cancel")
    keyboard.add(confirm_button)
    keyboard.add(cancel_button)
    bot.send_message(message.chat.id, "Хотите изменить пол?", reply_markup=keyboard)

def conformation(gender):
    if gender == "Мужчина":
        users_db.update({ "gender": gender }, { "$set": { "gender": "Женщина" } })
    else:
        users_db.update({ "gender": gender }, { "$set": { "gender": "Мужчина" } })


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    our_db_table = {}
    for x in users_db.find():
        if x['chat_id'] == call.message.chat.id:
            our_db_table = x
            break
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
        elif call.data == "male_gender":
            our_db_table['gender'] = 'Мужчина'
            users_db.update({"gender": None}, {"$set": {"gender": our_db_table['gender']}})
            main_menu(call.message)
        elif call.data == "female_gender":
            our_db_table['gender'] = 'Женщина'
            users_db.update({"gender": None}, {"$set": {"gender": our_db_table['gender']}})
            main_menu(call.message)
        elif call.data == "cancel":
            if not our_db_table['age']:
                age = our_db_table['forbidden_ages'].split(", ")[-1]
                users_db.update({'age': our_db_table['age']}, {"$set": {"age": age}})
            main_menu(call.message)


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
        bot.send_message(message.chat.id, 'Введите имя:')
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



if __name__ == '__main__':
    bot.polling(none_stop=True)
