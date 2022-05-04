import random
import telebot
from telebot import types
import main
from fpdf import FPDF
import datetime
from data import db_session
from data.lap import User
from data.names import Name
import mail
import promokod_mail


bot = telebot.TeleBot('5339971153:AAG_LkcuTX-Dtag1HelIhW1GC2Zqu8d51_w')
admin_arr = [5084780807, 1056884661]
db_session.global_init("db/users.db")
PROMOCOD = "LASTMEETING"


@bot.message_handler(commands=["start"])
def start(message, res=False):
    id = message.from_user.id
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(id))):
        nice_user = user
        bot.send_message(message.chat.id,
                         "Добрый день {}! \nЭтот бот предназначен для распознования текста с фотографии (.jpeg, .png, .pdf).".format(
                             nice_user.name[0].name))
        bot.send_message(message.chat.id,
                         "У нашего сервиса также есть подписка, с расширенными функциями.\nДля подробностей напишите /more.")
        break
    else:
        bot.send_message(message.chat.id,
                         "Добрый день! \nЭтот бот предназначен для распознования текста с фотографии (.jpeg, .png, .pdf).\nВведите свою почту для регистрации.")
        user = User()
        user.telegram_id = id
        user.hashed_password = 'ggg'
        user.user_status = 0
        user.username = message.from_user.username
        db_sess.add(user)
        db_sess.commit()
        name = Name()
        name.name = message.from_user.username
        name.user_id = user.id
        db_sess.add(name)
        db_sess.commit()


@bot.message_handler(commands=["more"])
def more(message):

    bot.send_message(message.chat.id,
                     "Расширенная версия нашего приложения включает:\n"
                     "- перевод текста почти с любого языка мира,\n"
                     "- возможность сохранения текста в pdf формате.")
    markup = types.InlineKeyboardMarkup()
    buttonB = types.InlineKeyboardButton('оплатить', callback_data='pay')
    markup.row(buttonB)
    bot.send_message(message.chat.id,
                     "Если Вам интересно наше предложение, нажмите 'оплатить'.", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "pay")
def payment(call):
    bot.send_message(call.message.chat.id, "Только сейчас дейтсвует специальное придложение - приведите друга и получи месяц использования"
                                           " сервиса бесплатно!")
    # stikers
    bot.send_message(call.message.chat.id,
                     "Для этого Ваш друг должен зарегистироваться в нашем сервисе. После этого Вы указываете его 'username' в этом чате и получаете промокод на почту.")
    bot.send_message(call.message.chat.id,
                     "Только сначала убедитесь, что у Вашего друга есть нужный параметр.")
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(call.message.chat.id))):
        user.wait_friend = True
        break
    db_sess.commit()


@bot.message_handler(commands=["mem"])
def mem(message):
    db_sess = db_session.create_session()
    if message.chat.id in admin_arr:
        for user in db_sess.query(User).all():
            with open("data/photo/memjpg.jpg", "rb") as f:
                bot.send_photo(user.telegram_id, f)


@bot.message_handler(content_types=["photo", "document", "text"])
def process(message):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(message.chat.id))):
        print(user.user_status)
        nice_user = user
        if nice_user.user_status == 0:
            email = message.text
            cod = str(random.randint(1000, 9999))
            cod_1 = 'Ваш код активации: ' + cod
            mail.main(email, cod_1)
            user.user_status = 1
            user.user_code = int(cod)
            user.email = email
            # Здесь должно сообщение на почту оправится
            bot.send_message(message.chat.id, "Введитe пароль, который отправлен на почту.")
            db_sess.commit()

        elif nice_user.user_status == 1:
            password = int(message.text)
            print(password)
            if password == user.user_code:
                user.created_date = datetime.datetime.now()
                user.user_status = 2
                db_sess.commit()
                bot.send_message(message.chat.id, 'Вы зарегистрировались! Можете присылать фотографии.')
                bot.send_message(message.chat.id,
                                 "У нашего сервиса также есть подписка, с расширенными функциями.\nДля подробностей напишите '/more'.")
            else:
                bot.send_message(message.chat.id, 'Пароль неверный, попробуйте заново.')

        else:
            if message.content_type == "photo" or message.content_type == "document":
                if message.content_type == "photo":
                    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                elif message.content_type == "document":
                    file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                user.file = downloaded_file
                db_sess.commit()
                if user.user_status == 2:
                    markup = types.InlineKeyboardMarkup()
                    buttonB = types.InlineKeyboardButton('txt', callback_data='txt')
                    buttonC = types.InlineKeyboardButton('текст в сообщение', callback_data='tx')
                    markup.row(buttonB, buttonC)
                    bot.send_message(message.chat.id, 'Выберите формат, в котором Вам прислать текст:',
                                     reply_markup=markup)
                if user.user_status == 3:
                    markup = types.InlineKeyboardMarkup()
                    buttonA = types.InlineKeyboardButton('pdf', callback_data='pdf')
                    buttonB = types.InlineKeyboardButton('txt', callback_data='txt')
                    buttonC = types.InlineKeyboardButton('текст в сообщение', callback_data='tx')
                    markup.row(buttonA, buttonB, buttonC)
                    bot.send_message(message.chat.id,
                                     'Мой господин, выберите формат текста в котором Вам прислать текст.',
                                     reply_markup=markup)
            if message.content_type == "text":
                if user.wait_friend:
                    for friend in db_sess.query(User).filter(User.username.like(message.text)):
                        if friend.created_date > user.created_date:
                            user.wait_friend = False
                            user.wait_promocod = True
                            bot.send_message(message.chat.id, "Отлично, теперь ждите промокод на почте и вводите его скорее!")
                            email = user.email
                            promokod_mail.main(email, 'Ваш промокод: ' + PROMOCOD)
                    if user.wait_friend:
                        bot.send_message(message.chat.id,
                                         'Вашего друга не найдено или он зарегистаровался раньше, чем Вы. Попробуйте ввести username заново')
                elif user.wait_promocod:
                    if message.text == PROMOCOD:
                        bot.send_message(message.chat.id, 'Поздравляем, Вы приобрели подписку. Пора оправлять фотографии.')
                        user.wait_promocod = False
                        user.user_status = 3
                else:
                    bot.send_message(message.chat.id, 'Боюсь Вы не поняли. Надо выслать фотографию, а я переводу её в текст.')
                db_sess.commit()


@bot.callback_query_handler(func=lambda call: call.data == "txt")
def handle_txt(call):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(call.message.chat.id))):
        if user.user_status == 2:
            bot.send_message(call.message.chat.id, 'Подождите секунду - происходит магия.')
            res = main.main(user.file, "ru")
            my_file = open("file.txt", "w+")
            my_file.write(res)
            my_file.close()
            with open("file.txt", "rb") as f:
                bot.send_document(call.message.chat.id, f)
        else:
            user.format = "txt"
            db_sess.commit()
            select_language(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "tx")
def handle_txt(call):
    bot.send_message(call.message.chat.id, 'Подождите секунду - происходит магия.')
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(call.message.chat.id))):
        if user.user_status == 2:
            res = main.main(user.file, call.message.text)
            bot.send_message(call.message.chat.id, res)
        else:
            user.format = "tx"
            db_sess.commit()
            select_language(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "pdf")
def handle_txt(call):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(call.message.chat.id))):
        user.format = "pdf"
        break
    db_sess.commit()
    select_language(call.message.chat.id)


def select_language(id):
    da= "🇩🇰"
    en = "🇬🇧"
    ru = "🇷🇺"
    es = "🇪🇸"
    fi = "🇫🇮"
    fr = "🇫🇷"
    de = "🇩🇪"
    markup = types.InlineKeyboardMarkup()
    buttonA = types.InlineKeyboardButton(ru, callback_data='ru')
    buttonB = types.InlineKeyboardButton(en, callback_data='en')
    buttonC = types.InlineKeyboardButton(fr, callback_data='fr')
    buttonD = types.InlineKeyboardButton(de, callback_data='de')
    buttonF = types.InlineKeyboardButton(fi, callback_data='fi')
    buttonE = types.InlineKeyboardButton(es, callback_data='es')
    buttonG = types.InlineKeyboardButton(da, callback_data='da')
    markup.row(buttonA, buttonB, buttonC, buttonD, buttonF, buttonE, buttonG)
    bot.send_message(id, 'Выберите язык, c которого перевести текст:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "da")
def callback_handler_ru(call):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(call.message.chat.id))):
        user.language = "da"
        break
    db_sess.commit()
    private(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "es")
def callback_handler_ru(call):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(call.message.chat.id))):
        user.language = "es"
        break
    db_sess.commit()
    private(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "fi")
def callback_handler_ru(call):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(call.message.chat.id))):
        user.language = "fi"
        break
    db_sess.commit()
    private(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "de")
def callback_handler_ru(call):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(call.message.chat.id))):
        user.language = "de"
        break
    db_sess.commit()
    private(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "ru")
def callback_handler_ru(call):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(call.message.chat.id))):
        user.language = "ru"
        break
    db_sess.commit()
    private(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "en")
def callback_handler_en(call):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(call.message.chat.id))):
        user.language = "en"
        break
    db_sess.commit()
    private(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "fr")
def callback_handler_fr(call):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(call.message.chat.id))):
        user.language = "fr"
        break
    db_sess.commit()
    private(call.message.chat.id)


def private(user_id):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.telegram_id.like(int(user_id))):
        bot.send_message(user_id, 'Подождите секунду - происходит магия.')
        res = main.main(user.file, user.language)
        print(res, user.format)
        if user.format == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font('DejaVu', '', 'data/ttf/DejaVuSansCondensed-BoldOblique.ttf', uni=True)
            pdf.set_font('DejaVu', '', 10)
            pdf.write(10, res)
            pdf.output("pdf.pdf")
            with open("pdf.pdf", "rb") as f:
                bot.send_document(user_id, f)
        elif user.format == "txt":
            my_file = open("file.txt", "w+")
            my_file.write(res)
            my_file.close()
            with open("file.txt", "rb") as f:
                bot.send_document(user_id, f)
        else:
            bot.send_message(user_id, res)
        bot.send_message(user_id, "Присылайте фотографии ещё, не бойтесь!")


bot.polling(none_stop=True, timeout=123)
