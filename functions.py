from telegram.ext import *
from telegram import *
import time
from constants import *
from lib import *


def telegram_id(update, context):
    chat_id = update.message.chat_id
    return chat_id


def first_name(update):
    f_name = update.message.from_user.first_name
    return f_name


def last_name(update):
    l_name = update.message.from_user.last_name
    return l_name


def hello_user(update, context):
    context.bot.send_message(chat_id=telegram_id(update, context), text=greeting_message)
    print(f"User ({telegram_id(update, context)})started the bot...")


def get_contact(update, context):
    contact_button = KeyboardButton("Telefon raqamni jo'natish ☎️", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
    context.bot.send_message(chat_id=telegram_id(update, context), text="Telefon raqamingizni yuboring",
                             reply_markup=reply_markup)


def next_step(update, context):
    user_message = update.message.contact
    print(user_message)