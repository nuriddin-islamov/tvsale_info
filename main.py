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

STATE_SIGNUP, STATE_USER, STATE_CLIENTS, STATE_FEEDBACK, STATE_ABOUT, STATE_PROMO, \
 STATE_ID1, STATE_ID1_CONTACT, STATE_ID1_ORDER = range(9)

conn = sqlite3.connect(database_path, check_same_thread=False)
cursor = conn.cursor()

# admin buttons
BTN_MAIL, GET_STATS, BACK_TO_ADMIN_MENU, BTN_BACK_TO_USER = (
    'start mailing', 'get stats', 'back to menu', 'back to user'
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
    name = cursor.execute("""
    SELECT name 
    FROM Users 
    WHERE telegram_id = '{}'
    """.format(telegram_id)).fetchone()
    return name[0]


# Select phone number of current user from database
def phone_of_user(update):
    telegram_id = update.message.chat_id
    phone = cursor.execute("""
    SELECT phone_number
    FROM Users
    WHERE telegram_id = '{}'
    """.format(telegram_id)).fetchone()
    return phone


# Greet the new user. Pass to the step of registration.
def start(update, context):
    user = update.message.from_user
    telegram_id = update.message.chat_id
    update.message.reply_html(greeting_message)
    db_id = cursor.execute("""SELECT ID FROM Users WHERE telegram_id = '{}'""".format(telegram_id)).fetchall()
    if len(db_id) == 0:
        logger.info("New user started the bot. Username: %s and F_Name: %s, L_Name: %s", user.username,
                    user.first_name, user.last_name)
        logs(update, f'New user started the bot. Username: {user.username}')
        time.sleep(0.99)
        update.message.reply_html(user_name)
        return STATE_SIGNUP
    else:
        logger.info('User %s continued using bot.', telegram_id)
        logs(update, f'User continued using bot')
        main_menu(update, context)
        return STATE_USER


# start registration for new user
def register(update, context):
    user = update.message.from_user
    username = user.username
    telegram_id = update.message.chat_id
    users_input = update.message.text
    unique_code = random.choice(alphabet) + '-' + str(random.randint(1000, 10000))
    cursor.execute("""
    INSERT INTO Users VALUES (NULL, '{}', '{}', '{}', 0, '{}')
    """.format(telegram_id, users_input, username, unique_code))
    conn.commit()
    logs(update, f"Registration started for {users_input} ({telegram_id})")
    logger.info("Registration started for %s (%s)", users_input, telegram_id)
    button = [[KeyboardButton(phone_send_btn, request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(button, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_html(request_phone, reply_markup=reply_markup)


def reg_complete(update, context):
    phone = update.message.contact['phone_number']
    user = update.message.from_user
    username = user.username
    telegram_id = update.message.chat_id
    cursor.execute("""
    UPDATE Users
    SET phone_number = '{}'
    WHERE telegram_id = '{}'
    """.format(phone, telegram_id))
    conn.commit()
    update.message.reply_html(registration_complete_msg)
    main_menu(update, context)
    logs(update, f'has been added to database. Phone: {phone}')
    logger.info("User %s has been added to database. Phone number: %s", telegram_id, phone)
    return STATE_USER


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
    update.message.reply_html(for_sponsors_text)
    logs(update, f"""{name_of_user(update)} pressed sposors button""")
    logger.info("Sponsors button pressed by %s (%s)", name_of_user(update), telegram_id)


def promo(update, context):
    update.message.reply_text(promo_text,
                              reply_markup=button_back)
    return STATE_PROMO


# Coming soon. Will be using this function during Ramadan
def ramadan(update, context):
    update.message.reply_text("ramazon tanlandi")


def help_menu(update, context):
    update.message.reply_text(help_text)


# def unknown_command(update, context):
#     update.message.reply_text("""Unknown command. Please choose proper command.
#
# /reset to reset the bot""")


def quit(update, context):
    update.message.reply_html("""
/user - continue as a user
/root - continue as an admin
    """, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# ----------------------- ADMIN CONFIGURATIONS START HERE --------------------- #


STATE_ADMIN, STATE_PASSWORD, MAILING = range(3)


def admin_sign_in(update, context):
    telegram_id = update.message.chat_id
    if telegram_id == 361516746 or 1025864881:
        update.message.reply_html('Enter password:', reply_markup=ReplyKeyboardRemove())
        return STATE_PASSWORD
    else:
        update.message.reply_html("Бу бўлим фақат админ учун 🚫")
        return STATE_USER


def check_password(update, context):
    password = update.message.text
    if password == 'nuriddin':
        update.message.reply_html("<b>Successful!</b>")
        admin_panel(update, context)
        return STATE_ADMIN
    else:
        update.message.reply_html("Try again...")


def admin_panel(update, context):
    update.message.reply_text('Welcome, boss!', reply_markup=ReplyKeyboardMarkup([
        [BTN_MAIL, GET_STATS], [BACK_TO_ADMIN_MENU], [BTN_BACK_TO_USER]],
        resize_keyboard=True))
    return STATE_ADMIN


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
    users = cursor.execute("""SELECT * FROM Users WHERE phone_number IN (998338789907, 998930086642) 
    """).fetchall()
    context.bot.send_message(chat_id=telegram_id,
                             text=message)


def back_to_user(update, context):
    update.message.reply_html('<i>Loading...</i>')
    time.sleep(0.5)
    main_menu(update, context)
# ----------------------- ADMIN CONFIGURATIONS END HERE --------------------- #


def reset(update, context):
    telegram_id = update.message.chat_id
    update.message.reply_html(reset_text, reply_markup=ReplyKeyboardRemove())
    logs(update, f"""reset for {name_of_user(update)}, ({telegram_id})""")
    logger.info("reset for %s, (%s)", name_of_user(update), telegram_id)


def main():
    updater = Updater(token=API_TOKEN, workers=100, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, run_async=True),
                      CommandHandler('user', start, run_async=True),
                      # CommandHandler('reset', main_menu, run_async=True)
                      ],
        states={
            STATE_SIGNUP: [
                MessageHandler(Filters.text, register, run_async=True),
                MessageHandler(Filters.contact, reg_complete, run_async=True)
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
            ]
        },
        fallbacks=[CommandHandler('menu', clients),
                   CommandHandler('start', main_menu),
                   CommandHandler('help', help_menu),
                   CommandHandler('quit', quit),
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
                MessageHandler(Filters.regex('^(' + BTN_BACK_TO_USER + ')$'), back_to_user)

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

    reset_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.all, reset, run_async=True)],
        states={},
        fallbacks=[conv_handler]
    )

    dispatcher.add_handler(root_handler)
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(reset_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
