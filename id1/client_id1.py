from lib import *
from main import *
from telegram.ext import *
from telegram import *

ID1_MALUMOT, ID1_BUYURTMA, ID1_MUTAXASSIS, ID1_SAXIFALAR = (
    '📃 Маълумот олиш', '📥 Буюртма бериш', '🗯 Мутаҳассис билан боғланиш', '📲 Ижтимоий тармоқлар'
)
buttons_id1 = ReplyKeyboardMarkup([
    [ID1_MALUMOT, ID1_BUYURTMA], [ID1_MUTAXASSIS, ID1_SAXIFALAR], [BACK]
], resize_keyboard=True)


def info(update, context):
    update.message.reply_html(id1_info)


def social(update, context):
    update.message.reply_html(id1_social, disable_web_page_preview=True)


def contact(update, context):
    update.message.reply_html(id1_contact, reply_markup=button_back)
    return STATE_ID1_CONTACT


def id1_feedback(update, message):
    telegram_id = update.message.chat_id
    msg = update.message.text
    phone = cursor.execute("""SELECT phone_number FROM Users WHERE telegram_id = '{}'
    """.format(telegram_id)).fetchone()
    name = cursor.execute("""SELECT name FROM Users WHERE telegram_id = '{}'
    """.format(telegram_id)).fetchone()
    f = open('id1/id1_fdbck.txt', 'a')
    f.write(f"""Пользователь:
    {time.asctime()}
    Имя: {name[0]};
    Телефон: {phone[0]};
    Telegram_ID: {telegram_id};
    
    Сообщение: {msg}
    \n\n""")
    f.close()
    update.message.reply_html(accepted_id1.format(name_of_user(update)))


def order(update, context):
    update.message.reply_html("order selected")


