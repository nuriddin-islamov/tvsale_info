from telegram.files import file
from configs import *
from telegram.ext import *
from urls import *
from telegram import *
from lib import *
import time
import logging
import random
import sqlite3
from id1.client_id1 import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

STATE_SIGNUP, STATE_USER, STATE_CLIENTS, STATE_FEEDBACK, STATE_ABOUT, STATE_PROMO, REQUEST_CONTACT, \
 STATE_ID1, STATE_ID1_CONTACT, STATE_ID1_ORDER, STATE_PARTNERSHIP = range(11)

conn = sqlite3.connect(database_path, check_same_thread=False)
cursor = conn.cursor()

# admin buttons
BTN_MAIL, GET_STATS, BACK_TO_ADMIN_MENU, BTN_LOG_OUT = (
    'start mailing', 'get stats', 'back to menu', 'log out'
)
# main menu buttons
BTN_CLIENTS, BTN_ABOUT, BTN_FEEDBACK, BTN_FOR_SPONSORS, BTN_PROMO, BTN_RAMADAN = (
    "🛍 Маҳсулот ва хизматлар", "ℹ️ Биз ҳақимизда", "💬 Алоқа учун", "🤝 Ҳамкорлик учун", "💝 Промо-кодлар", "Ramazon"
)
main_buttons = ReplyKeyboardMarkup([
    [BTN_CLIENTS], [BTN_FOR_SPONSORS, BTN_PROMO], [BTN_ABOUT, BTN_FEEDBACK]
], resize_keyboard=True)

ID_1, ID_2, ID_3, ID_4, BACK = (
    '🧬 Лактовита', '♻️ Массажёр', '🏥 «Real Medical» тиббиёт маркази', '🔥 Газ фильтр', '⬅️ Орқага'
)
client_buttons = ReplyKeyboardMarkup([
    [ID_1, ID_2], [ID_3, ID_4], [BACK]
], resize_keyboard=True)

button_back = ReplyKeyboardMarkup([
    [KeyboardButton(BACK)]
], resize_keyboard=True)


# Save logs into logs.txt file
def logs(update, message):
    telegram_id = update.message.chat_id
    f = open('logs.txt', 'a')
    f.write(f'''{time.asctime()} - {telegram_id} - {message} \n''')
    f.close()


# Select name of current user from database
def name_of_user(update):
    telegram_id = update.message.chat_id
    name_db = cursor.execute("""
    SELECT name 
    FROM Users 
    WHERE telegram_id = '{}'
    """.format(telegram_id)).fetchone()
    return name_db[0]


# Select phone number of current user from database
def phone_of_user(update):
    telegram_id = update.message.chat_id
    phone = cursor.execute("""
    SELECT phone_number
    FROM Users
    WHERE telegram_id = '{}'
    """.format(telegram_id)).fetchone()
    return phone[0]


def loading(update, context):
    time.sleep(0.99)
    load = update.message.reply_html('''Хмм''')
    i = 0
    while i < 1:
        time.sleep(0.2)
        load.edit_text('Хмм🧐')
        time.sleep(0.5)
        load.edit_text('Хмм🧐🧐')
        time.sleep(0.5)
        load.edit_text('Хмм🧐🧐🧐')
        time.sleep(0.6)
        load.edit_text('Хмм🧐🧐🧐🧐')
        time.sleep(0.5)
        load.edit_text('Хмм🧐🧐🧐🧐..')
        time.sleep(0.9)
        i += 1
        load.edit_text('Хмм🤔')
        time.sleep(0.5)
        load.edit_text('Хмм🤔🤔')
        time.sleep(0.3)
        load.edit_text('Хмм🤔🤔🤔')
        time.sleep(0.6)
        load.edit_text('Хмм🤔🤔🤔🤔')
        time.sleep(0.1)
        i += 1


# Greet the new user. Pass to the step of registration.
def start(update, context):
    user = update.message.from_user
    telegram_id = update.message.chat_id
    db_id = cursor.execute("""SELECT telegram_id FROM Users WHERE telegram_id = '{}'""".format(telegram_id)).fetchall()
    code = cursor.execute("SELECT stage_id FROM Users WHERE telegram_id = '{}'".format(telegram_id)).fetchone()
    if len(db_id) == 0 or code[0] == str(0):
        update.message.reply_html(greeting_message, reply_markup=ReplyKeyboardRemove())
        logger.info("New user started the bot. Username: %s and F_Name: %s, L_Name: %s", user.username,
                    user.first_name, user.last_name)
        logs(update, f'New user started the bot. Username: {user.username}')
        loading(update, context)
        registration_start(update, context)
        return STATE_SIGNUP
    elif code[0] == str(1):
        request_contact(update, context)
        return REQUEST_CONTACT
    else:
        logger.info('User %s continued using bot.', telegram_id)
        logs(update, f'User continued using bot')
        main_menu(update, context)
        return STATE_USER


def registration_start(update, context):
    telegram_id = update.message.chat_id
    user = update.message.from_user
    table_id = cursor.execute("SELECT ID From Users WHERE telegram_id = '{}'".format(telegram_id)).fetchone()
    if table_id is None:
        cursor.execute("""INSERT INTO Users VALUES (NULL, '{}', 0, '{}', 0, 0, 0)
        """.format(telegram_id, user.username))
        conn.commit()
    update.message.reply_html(registration_start_txt)


def request_contact(update, context):
    button = [[KeyboardButton(phone_send_btn, request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(button, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_html(request_phone.format(name_of_user(update)), reply_markup=reply_markup)


def check_name(update, context):
    telegram_id = update.message.chat_id
    user_input = update.message.text
    name = user_input.split()
    if len(name) == 2:
        if name[0][0].isupper() and name[1][0].isupper():
            cursor.execute("""UPDATE Users SET name = '{}', stage_id = '{}' WHERE telegram_id = '{}'
            """.format(user_input, 1, telegram_id))
            conn.commit()
            update.message.reply_html(accepted_name_txt)
            request_contact(update, context)
            return REQUEST_CONTACT
        else:
            update.message.reply_html(name_with_capitals)
    else:
        update.message.reply_html(please_full_name)


def check_phone(update, context):
    telegram_id = update.message.chat_id
    user_phone = update.message.contact['phone_number']
    unique_code = random.randint(100000, 1000000)
    cursor.execute("""
            UPDATE Users
            SET phone_number = '{}', unique_code = '{}', stage_id = '{}'
            WHERE telegram_id = '{}'
            """.format(user_phone, unique_code, 2, telegram_id))
    conn.commit()
    update.message.reply_html(registration_complete_msg)
    logs(update, f'has been added to database. Phone: {user_phone}')
    logger.info("User %s has been added to database. Phone number: %s", telegram_id, user_phone)
    main_menu(update, context)
    return STATE_USER


def check_phone_text(update, context):
    telegram_id = update.message.chat_id
    user_input = update.message.text
    listed = list(user_input)
    phone_filter = listed[1:]
    number = ''.join(i for i in phone_filter)
    if number[:3] == '998' and len(number) == 12:
        unique_code = random.randint(100000, 1000000)
        cursor.execute("""
            UPDATE Users
            SET phone_number = '{}', unique_code = '{}', stage_id = '{}'
            WHERE telegram_id = '{}'
            """.format(number, unique_code, 2, telegram_id))
        conn.commit()
        update.message.reply_html(registration_complete_msg)
        logs(update, f'has been added to database. Phone: {number}')
        logger.info("User %s has been added to database. Phone number: %s", telegram_id, number)
        time.sleep(0.5)
        main_menu(update, context)
        return STATE_USER
    else:
        update.message.reply_html(correct_phone_text)


def main_menu(update, context):
    update.message.reply_html(main_menu_text, reply_markup=main_buttons)
    telegram_id = update.message.chat_id
    logs(update, f"main menu opened by {name_of_user(update)}")
    logger.info("%s main menu opened by %s", telegram_id, name_of_user(update))
    return STATE_USER


def clients(update, context):
    update.message.reply_html(clients_choose_text, reply_markup=client_buttons)
    telegram_id = update.message.chat_id
    logs(update, f"clients menu opened by {name_of_user(update)}")
    logger.info("%s clients menu opened by %s", telegram_id, name_of_user(update))
    return STATE_CLIENTS


def id_1(update, context):
    chat_id = update.message.chat_id
    update.message.reply_photo(lactovita_pic, caption='''<b>«Lactovita» шифобахш маҳсулоти</b>''',
                               parse_mode='HTML', reply_markup=buttons_id1)
    telegram_id = update.message.chat_id
    logs(update, f"id_1 menu opened")
    logger.info("%s id_1 menu opened", telegram_id)
    return STATE_ID1


def id_2(update, context):
    update.message.reply_photo(massajor_pic, caption='''<b>«VEST BRAUN SHOP» массажёрлари</b>

☎️ Телефон рақамлар:
• 70-983-28-83''', parse_mode='HTML')
    telegram_id = update.message.chat_id
    logs(update, f"id_2 pressed")
    logger.info("%s id_2 pressed", telegram_id)


def id_3(update, context):
    update.message.reply_photo(real_medical_pic, caption='''<b>«Real Medical» тиббиёт маркази</b>

☎️ Телефон рақамлар:
• 97-241-03-03
• 97-249-03-03''', parse_mode='HTML')
    telegram_id = update.message.chat_id
    logs(update, f"id_3 pressed")
    logger.info("%s id_3 pressed", telegram_id)


def id_4(update, context):
    update.message.reply_photo(gazfiltr_pic, caption='''<b>«Safety» газ фильтрлари</b>

☎️ Телефон рақамлар:
• 71-200-48-88''', parse_mode='HTML')
    telegram_id = update.message.chat_id
    logs(update, f"id_4 pressed")
    logger.info("%s id_4 pressed", telegram_id)


def back_to_menu(update, context):
    telegram_id = update.message.chat_id
    main_menu(update, context)
    logs(update, f"back to main menu")
    logger.info("%s back to main menu", telegram_id)
    return STATE_USER


def back_to_clients(update, context):
    telegram_id = update.message.chat_id
    clients(update, context)
    logs(update, f"back to clients menu")
    logger.info("%s back to clients menu", telegram_id)
    return STATE_CLIENTS


def about(update, context):
    update.message.reply_html(about_text,
                              reply_markup=button_back)
    return STATE_ABOUT


def feedback(update, context):
    update.message.reply_text(feedback_text,
                              reply_markup=button_back)
    telegram_id = update.message.chat_id
    logs(update, f"feedback section opened by {name_of_user(update)}")
    logger.info("%s feedback section opened by %s", telegram_id, name_of_user(update))
    return STATE_FEEDBACK


def get_feedback(update, context):
    feedback_message_from_user = update.message.text
    telegram_id = update.message.chat_id
    f = open('feedbacks.txt', 'a')
    f.write(f"""User:
    {time.asctime()}
    Name: {name_of_user(update)};
    Phone number: {phone_of_user(update)};
    Telegram_ID: {telegram_id};
    
    Message: {feedback_message_from_user}
    \n\n""")
    f.close()
    logs(update, f"{name_of_user(update)} has just sent a feedback")
    logger.info("%s - %s has just sent a feedback", telegram_id, name_of_user(update))
    update.message.reply_html(feedback_accepted_text)


def for_sponsors(update, context):
    telegram_id = update.message.chat_id
    update.message.reply_html(for_sponsors_text, reply_markup=ReplyKeyboardMarkup([[BACK]], resize_keyboard=True))
    logs(update, f"""{name_of_user(update)} pressed sposors button""")
    logger.info("Sponsors button pressed by %s (%s)", name_of_user(update), telegram_id)
    return STATE_PARTNERSHIP


def promo(update, context):
    update.message.reply_text(promo_text,
                              reply_markup=button_back)
    return STATE_PROMO


# Coming soon. Will be using this function during Ramadan
def ramadan(update, context):
    update.message.reply_text("ramazon tanlandi")


def help_menu(update, context):
    update.message.reply_text(help_text)


def send_commercial(update, context):
    telegram_id = update.message.chat_id
    message = update.message.text
    if message == '0123456':
        context.bot.send_document(chat_id=telegram_id,
                                  document='BQACAgIAAxkBAAITVWA6m8BhBbg58UJgdT-TegfUbXXzAALCDAACaEvYSUpwoD4v0px4HgQ')
        f = open('commercials_got.txt', 'a')
        f.write(f"""User:
        {time.asctime()}
        Name: {name_of_user(update)};
        Phone number: {phone_of_user(update)};
        Telegram_ID: {telegram_id};
        
        GOT COMMERCIAL.
        \n""")
        f.close()
    else:
        update.message.reply_html('Нотўғри белгилар терилди!')


# def unknown_command(update, context):
#     update.message.reply_text("""Unknown command. Please choose proper command.
#
# /reset to reset the bot""")


def quit(update, context):
    update.message.reply_html("""
/user - continue as a user
/root - continue as root
    """, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# ----------------------- ADMIN CONFIGURATIONS START HERE --------------------- #


STATE_ADMIN, STATE_PASSWORD, MAILING = range(3)


def back_to_login(update, context):
    text = update.message.reply_html('Loading')
    i = 0
    while i < 1:
        text.edit_text('Loading.')
        time.sleep(0.5)
        text.edit_text('Loading..')
        time.sleep(0.5)
        text.edit_text('Loading...')
        time.sleep(0.5)
        i += 1
    quit(update, context)
    return ConversationHandler.END


def admin_sign_in(update, context):
    telegram_id = update.message.chat_id
    stage_id = cursor.execute("""SELECT stage_id FROM Users WHERE telegram_id = '{}'""".format(telegram_id)).fetchone()
    conn.commit()
    admin_pass = int(stage_id[0])
    if admin_pass == 99:
        update.message.reply_html('Enter password:', reply_markup=ReplyKeyboardRemove())
        return STATE_PASSWORD
    else:
        update.message.reply_html("Бу бўлим фақат админ учун 🚫")


def check_password(update, context):
    password = update.message.text
    if password == 'nuriddin':
        update.message.reply_html("Successful!")
        root_login(update, context)
        return STATE_ADMIN
    else:
        update.message.reply_html("Try again...")


def admin_panel(update, context):
    telegram_id = update.message.chat_id
    update.message.reply_text(f'Welcome, {name_of_user(update)}!', reply_markup=ReplyKeyboardMarkup([
        [BTN_MAIL, GET_STATS], [BTN_LOG_OUT]],
        resize_keyboard=True))
    return STATE_ADMIN


def root_login(update, context):
    telegram_id = update.message.chat_id
    update.message.reply_html(f"""
New login on {time.asctime()}

TvSale bot Admin Panel. (c) V 1.0

Welcome!

<i>User info:</i>
- Telegram ID: <b>{update.message.chat_id}</b>
- Name: <b>{name_of_user(update)}</b>
""")
    admin_panel(update, context)


def mailing_menu(update, context):
    update.message.reply_text('''Send me a message and I will send it back to you.
In real cases, I will send your message to everyone subscribed to me.

Don't forget I am a bot.''', reply_markup=ReplyKeyboardMarkup([
        ['Back']
    ], resize_keyboard=True))
    return MAILING


def send_mailing(update, context):
    message = update.message.text
    telegram_id = update.message.chat_id
    stage_id = cursor.execute("""SELECT telegram_id FROM Users WHERE stage_id == '2' 
    """).fetchall()
    users = list(stage_id[0])
    print(stage_id[0])
    print(users)
    context.bot.send_message(chat_id=telegram_id,
                             text=message)


def get_stat(update, context):
    telegram_id = update.message.chat_id
    pass


# ----------------------- ADMIN CONFIGURATIONS END HERE --------------------- #


def reset(update, context):
    telegram_id = update.message.chat_id
    update.message.reply_html(reset_texts[random.randint(0, len(reset_texts))], reply_markup=ReplyKeyboardRemove())
    logs(update, f"""reset for {name_of_user(update)}, ({telegram_id})""")
    logger.info("reset for %s, (%s)", name_of_user(update), telegram_id)


def main():
    updater = Updater(token=API_TOKEN, workers=100, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, run_async=True),
                      CommandHandler('user', main_menu, run_async=True),
                      MessageHandler(Filters.all, start)
                      ],
        states={
            STATE_SIGNUP: [
                MessageHandler(Filters.text, check_name, run_async=True)
            ],
            REQUEST_CONTACT: [
                MessageHandler(Filters.text, check_phone_text, run_async=True),
                MessageHandler(Filters.contact, check_phone, run_async=True)
            ],
            STATE_USER: [
                MessageHandler(Filters.regex('^(' + BTN_CLIENTS + ')$'), clients),
                MessageHandler(Filters.regex('^(' + BTN_ABOUT + ')$'), about),
                MessageHandler(Filters.regex('^(' + BTN_FEEDBACK + ')$'), feedback),
                MessageHandler(Filters.regex('^(' + BTN_FOR_SPONSORS + ')$'), for_sponsors),
                MessageHandler(Filters.regex('^(' + BTN_PROMO + ')$'), promo)

                # MessageHandler(Filters.regex('^(' + BTN_RAMADAN + ')$'), ramadan)
            ],
            STATE_CLIENTS: [
                MessageHandler(Filters.regex('^(' + ID_1 + ')$'), id_1),
                MessageHandler(Filters.regex('^(' + ID_2 + ')$'), id_2),
                MessageHandler(Filters.regex('^(' + ID_3 + ')$'), id_3),
                MessageHandler(Filters.regex('^(' + ID_4 + ')$'), id_4),
                MessageHandler(Filters.regex('^(' + BACK + ')$'), back_to_menu)
            ],
            STATE_ID1: [
                MessageHandler(Filters.regex('^(' + ID1_MALUMOT + ')$'), info),
                MessageHandler(Filters.regex('^(' + ID1_BUYURTMA + ')$'), order),
                MessageHandler(Filters.regex('^(' + ID1_MUTAXASSIS + ')$'), contact),
                MessageHandler(Filters.regex('^(' + ID1_SAXIFALAR + ')$'), social),
                MessageHandler(Filters.regex('^(' + BACK + ')$'), back_to_clients)
            ],
            STATE_ID1_CONTACT: [
                MessageHandler(Filters.regex('^(' + BACK + ')$'), id_1),
                MessageHandler(Filters.text, id1_feedback)
            ],
            STATE_ID1_ORDER: [

            ],
            STATE_FEEDBACK: [
                MessageHandler(Filters.regex('^(' + BACK + ')$'), back_to_menu),
                MessageHandler(Filters.all, get_feedback)
            ],
            STATE_ABOUT: [
                MessageHandler(Filters.regex('^(' + BACK + ')$'), back_to_menu)
            ],
            STATE_PROMO: [
                MessageHandler(Filters.regex('^(' + BACK + ')$'), back_to_menu)
            ],
            STATE_PARTNERSHIP: [
                MessageHandler(Filters.regex('^(' + BACK + ')$'), back_to_menu),
                MessageHandler(Filters.all, send_commercial)
            ]
        },
        fallbacks=[CommandHandler('menu', clients),
                   CommandHandler('start', main_menu),
                   CommandHandler('help', help_menu),
                   CommandHandler('quit', quit),
                   CommandHandler('logout', quit),
                   MessageHandler(Filters.all, main_menu)]
    )
    root_handler = ConversationHandler(
        entry_points=[CommandHandler('root', admin_sign_in)],
        states={
            # ------------- ADMIN STATES ------------- #
            STATE_PASSWORD: [
                MessageHandler(Filters.text, check_password)
            ],
            STATE_ADMIN: [
                MessageHandler(Filters.regex('^(' + BTN_MAIL + ')$'), mailing_menu),
                MessageHandler(Filters.regex(GET_STATS), get_stat),
                MessageHandler(Filters.regex('^(' + BTN_LOG_OUT + ')$'), back_to_login)

            ],
            MAILING: [
                MessageHandler(Filters.regex('^(' + 'Back' + ')$'), admin_panel),
                MessageHandler(Filters.text, send_mailing)
            ]

        },
        fallbacks=[CommandHandler('quit', quit),
                   MessageHandler(Filters.all, admin_panel),
                   ]
    )

    # reset_handler = ConversationHandler(
    #     entry_points=[MessageHandler(Filters.all, reset, run_async=True)],
    #     states={},
    #     fallbacks=[conv_handler]
    # )

    dispatcher.add_handler(root_handler)
    dispatcher.add_handler(conv_handler)
    # dispatcher.add_handler(reset_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
