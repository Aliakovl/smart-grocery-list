import datetime

from telebot import types, TeleBot
from os import getenv
from src.main.model.model import *
from datetime import date
# import calendar
from src.main.mongo.mongo_db import *
from src.main.model.recipe_parser import ParserRecipe

TOKEN = getenv('TELEGRAM_TOKEN')
bot = TeleBot(token=TOKEN)
day_name = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


def make_init_buttons():
    init_markup = types.ReplyKeyboardMarkup(False, True)
    start_button = types.KeyboardButton('/start')
    # init_button = types.KeyboardButton('Помощь')
    init_markup.row(start_button)
    # init_markup.row(init_button)
    return init_markup


def make_days_buttons():
    makeup = types.ReplyKeyboardMarkup(True, True)
    one = types.KeyboardButton("1")
    two = types.KeyboardButton("2")
    tree = types.KeyboardButton("3")
    four = types.KeyboardButton("4")
    five = types.KeyboardButton("5")
    six = types.KeyboardButton("6")
    seven = types.KeyboardButton("7")
    eight = types.KeyboardButton("8")
    nine = types.KeyboardButton("9")
    makeup.row(one, two, tree)
    makeup.row(four, five, six)
    makeup.row(seven, eight, nine)
    return makeup


def next_day_button():
    makeup = types.ReplyKeyboardMarkup(True, False)
    next_day = types.KeyboardButton("/next_day")
    makeup.row(next_day)
    return makeup


def add_product_button():
    makeup = types.ReplyKeyboardMarkup(True, False)
    generate_list = types.KeyboardButton("/generate_list")
    show_recipes = types.KeyboardButton("/show_recipes")
    makeup.row(generate_list)
    makeup.row(show_recipes)
    return makeup


make_init_buttons()


@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    make_new_user(user_id)
    print_all_user_info(user_id)
    bot.send_message(message.from_user.id, "На сколько дней вперёд вы планируете меню?", reply_markup=make_days_buttons())


@bot.message_handler(regexp=r'(^\d+$)')
def number_handler(message):
    user_id = message.from_user.id
    print(message)
    # print(get_user_state(user_id))
    if get_user_state(user_id) == 1:
        set_user_state(user_id, 2)
        set_user_n_days(user_id, int(message.text))
        set_user_day(user_id, int(message.text) - 1)
        my_date = date.today()
        print(my_date)
        day_nm = day_name[my_date.weekday()]
        print(my_date.weekday())
        bot.send_message(message.from_user.id, f"Добавте ссылки на рецепты {day_nm}", reply_markup=next_day_button())


@bot.message_handler(commands=['next_day'])
def next_day_handler(message):
    user_id = message.from_user.id
    print(message)
    if get_user_state(user_id) == 2:
        if get_user_day(user_id) > 0:
            n_day = get_user_n_days(user_id) - get_user_day(user_id)
            next_day = date.today() + datetime.timedelta(days=n_day)
            print(next_day)
            print(next_day.weekday())
            day_nm = day_name[next_day.weekday()]
            bot.send_message(message.from_user.id, f"Добавте ссылки на рецепты {day_nm}",
                             reply_markup=next_day_button())
            decrease_user_day(user_id)
        else:
            set_user_state(user_id, 3)
            bot.send_message(message.from_user.id, f"Что ещё добавить в список покупок?",
                             reply_markup=add_product_button())


@bot.message_handler(commands=['generate_list'])
def generate_list_handler(message):
    user_id = message.from_user.id
    print(message)
    if get_user_state(user_id) == 3:
        set_user_state(user_id, 4)
        bot.send_message(message.from_user.id, "Cписок покупок")


@bot.message_handler(commands=['show_recipes'])
def show_recipes_handler(message):
    user_id = message.from_user.id
    print(message)
    if get_user_state(user_id) == 3:
        set_user_state(user_id, 4)
        recipes, days = give_all_recipes(user_id)
        for day, day_n in days.items():
            keyboard = types.InlineKeyboardMarkup(row_width=len(days))
            for recipe, uri in recipes[day].items():
                keyboard.add(types.InlineKeyboardButton(text=recipe, url=uri))
            bot.send_message(message.from_user.id, f'{day_n}:   {day}', reply_markup=keyboard)


@bot.message_handler(func=lambda message: 'entities' in message.json and message.json['entities'][0]['type'] == 'url')
def link_handler(message):
    print(message.text)
    user_id = message.from_user.id
    if get_user_state(user_id) == 2:
        if get_user_day(user_id) >= 0:
            n_day = get_user_n_days(user_id) - get_user_day(user_id) - 1
            next_day = date.today() + datetime.timedelta(days=n_day)
            print(next_day)
            print(next_day.weekday())
            day_nm = day_name[next_day.weekday()]
            parser = ParserRecipe(message.text)
            ingredients = parser.pipe()
            products = [make_product(*ingredient) for ingredient in ingredients]
            description = message.text
            name = parser.get_name()
            add_new_day(user_id, str(next_day), str(day_nm), make_new_recipe(name, description, products))


@bot.message_handler(regexp=r'(.*)')
def start_command(message):
    bot.send_message(message.chat.id, "Hello!")
    print(bot.get_me())


@bot.message_handler(content_types=['photo'])
def start_command(message):
    file_id = message.json['photo'][-1]['file_id']
    print(bot.get_file(file_id))
    print(bot.get_file_url(file_id))
    print(file_id)


if __name__ == '__main__':
    # parser = ParserRecipe('https://povar.ru/recipes/sup_harcho_iz_baraniny_klassicheskii-57059.html')
    # ingredients = parser.pipe()

    bot.polling()
