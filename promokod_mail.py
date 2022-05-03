import smtplib
from email.mime.text import MIMEText


def send_email(email, message):
    sender = 'translator.bot.tg@gmail.com'
    password = 'translatorbottg'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:

        server.login(sender, password)
        msg = MIMEText(message)
        msg['Subject'] = 'Промокод:'
        server.sendmail(sender, email, msg.as_string())
    except Exception as ex:
        print(ex)


def main(email, message):
    send_email(email, message)