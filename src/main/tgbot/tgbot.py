import datetime

from telebot import types, TeleBot
from os import getenv
from datetime import date
from src.main.mongo.mongo_db import *
from src.main.model.recipe_parser import ParserRecipe
from src.main.model.typos_search import *


TOKEN = getenv('TELEGRAM_TOKEN')
bot = TeleBot(token=TOKEN)
day_name = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
pieces = ['шт', 'штуки', 'штука', 'штук']
grams = ['г', 'гр', 'грамм', 'грамма']
kilograms = ['кг', 'кило', 'килограмм', 'килограмма']
milliliters = ['мл', 'миллилитр', 'миллилитра', 'миллилитров']

tea_spoon = ['чайная ложка', 'ч. ложка', 'чайн. ложка', 'чайная л', 'ч. ложек']
table_spoon = ['столовая ложка', 'ст. ложка', 'стол. ложка', 'столовая л', 'cт. ложек']
glass = ['стакан', 'стак', 'ст']

dict_for_glass = {
    'сахар': '200',
    'крахмал': '160',
    'мука': '160',
    'молоко': '250',
    'мед': '415',
    'масло': '225',
    'вода': '200',
    'сливки': '230',
    'сметана': '230',
    'рис': '180',
    'гречка': '165',
    'манка': '160'
}
dict_for_tablespoon = {
    'сахар': '25',
    'крахмал': '12',
    'мука': '25',
    'молоко': '20',
    'мед': '30',
    'масло': '17',
    'желатин': '10',
    'сода': '8.5',
    'томатная паста': '24',
    'соль': '30'

}
dict_for_teaspoon = {
    'сахар': '8',
    'крахмал': '6',
    'мука': '8',
    'молоко': '5',
    'мед': '9',
    'масло': '5',
    'соль': '10'
}
dict_of_products = {
    'стакан': dict_for_glass,
    'столовая ложка': dict_for_tablespoon,
    'чайная ложка': dict_for_teaspoon
}
liquid = ['молоко', 'растительное масло', 'вода', 'сливки', 'кефир', 'коньяк', 'вино', 'уксус']

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
    add_available_products = types.KeyboardButton("/i_have_some")
    makeup.row(generate_list)
    makeup.row(show_recipes)
    makeup.row(add_available_products)
    return makeup


make_init_buttons()


@bot.message_handler(commands=['i_have_some'])
def i_have_some_handler(message):
    user_id = message.from_user.id


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
        print(give_grocery_list(user_id))
        grocery_list = give_grocery_list(user_id)
        for product, pair in grocery_list.items():
            quantity, units = pair[0], pair[1]
            print(quantity)
            if quantity >= 1000:
                quantity /= 1000
                units = kilograms[0]
            if units == 'none':
                bot.send_message(message.from_user.id, f'{product}')
            else:
                bot.send_message(message.from_user.id, f'{product}: {float(quantity):g} {units}')


@bot.message_handler(commands=['show_recipes'])
def show_recipes_handler(message):
    user_id = message.from_user.id
    print(message)
    if get_user_state(user_id) == 3:
        recipes, days = give_all_recipes(user_id)
        for day, day_n in days.items():
            keyboard = types.InlineKeyboardMarkup(row_width=len(days))
            for recipe, uri in recipes[day].items():
                keyboard.add(types.InlineKeyboardButton(text=recipe, url=uri))
            bot.send_message(message.from_user.id, f'{day_n}:   {day}', reply_markup=keyboard)


# convert measure and quality to grams or milliliters.
def unification(ingrt, quantity, measure):
    print(ingrt)
    new_quantity = quantity
    found = False

    if find_typos(measure, tea_spoon):
        if ingrt in dict_of_products['чайная ложка']:
            quan = dict_of_products['чайная ложка'][ingrt]
        else:
            quan = '10'
        new_quantity = float(quan) * quantity
        found = True

    if find_typos(measure, table_spoon):
        if ingrt in dict_of_products['столовая ложка']:
            quan = dict_of_products['столовая ложка'][ingrt]
        else:
            quan = '20'
        new_quantity = float(quan) * quantity
        found = True

    if find_typos(measure, glass):
        if ingrt in dict_of_products['стакан'][ingrt]:
            quan = dict_of_products['стакан'][ingrt]
        else:
            quan = '250'
        new_quantity = float(quan) * quantity
        found = True

    if found:
        if ingrt in liquid:
            return ingrt, new_quantity, 'мл'
        else:
            return ingrt, new_quantity, 'г'
    else:
        if find_typos(measure, pieces):
            return ingrt, quantity, pieces[0]
        if find_typos(measure, grams):
            return ingrt, quantity, grams[0]
        if find_typos(measure, kilograms):
            return ingrt, quantity, kilograms[0]
        if find_typos(measure, milliliters):
            return ingrt, quantity, milliliters[0]
        return ingrt, quantity, 'none'


@bot.message_handler(func=lambda message: 'entities' in message.json and message.json['entities'][0]['type'] == 'url')
def link_handler(message):
    print(message.text)
    begin = message.json['entities'][0]['offset']
    end = begin + message.json['entities'][0]['length']
    url = message.text[begin:end]
    print(url)
    user_id = message.from_user.id
    if get_user_state(user_id) == 2:
        if get_user_day(user_id) >= 0:
            n_day = get_user_n_days(user_id) - get_user_day(user_id) - 1
            next_day = date.today() + datetime.timedelta(days=n_day)
            print(next_day)
            print(next_day.weekday())
            day_nm = day_name[next_day.weekday()]
            parser = ParserRecipe(url)
            ingredients = parser.pipe()
            products = []
            for name, quantity, units in ingredients:
                name, quantity, u_units = unification(name, quantity, units)
                if u_units == kilograms[0]:
                    quantity *= 1000
                    u_units = grams[0]
                products.append(make_product(name, quantity, u_units))
            description = url
            name = parser.get_name()
            add_new_day(user_id, str(next_day), str(day_nm), make_new_recipe(name, description, products))


@bot.message_handler(regexp=r'(.*)')
def start_command(message):
    bot.send_message(message.chat.id, "Я не понимаю :(")
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
