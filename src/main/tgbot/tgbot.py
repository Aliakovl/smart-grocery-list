from telebot import types, TeleBot
from os import getenv

TOKEN = getenv('TELEGRAM_TOKEN')
bot = TeleBot(token=TOKEN)


markup = types.ReplyKeyboardMarkup(True, False)
add_recipe_button = types.KeyboardButton('Добавить рецепт')
add_item_button = types.KeyboardButton('Добавить продукт')
markup.row(add_recipe_button)
markup.row(add_item_button)


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "На сколько дней вперёд вы планируете меню", reply_markup=markup)
    # bot.send_message(message.chat.id, "Выбери действие", reply_markup=markup)


@bot.message_handler(regexp=r'(.*)')
def start_command(message):
    print(message)
    bot.send_message(message.chat.id, "Hello!")
    print(bot.get_me())


@bot.message_handler(content_types=['photo'])
def start_command(message):
    file_id = message.json['photo'][-1]['file_id']
    print(bot.get_file(file_id))
    print(bot.get_file_url(file_id))
    print(file_id)


if __name__ == '__main__':
    bot.polling()
