
import telegram
from telegram.ext import Updater
from telegram.ext import Dispatcher
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import PicklePersistence
from json import dumps
import sqlite3
import logging

# TODO: Man kann ohne sich in die Benutzerliste einzutragen dem Bot schreiben


# Wenn jemand den Chat löscht: Aus user-Liste austragen

def start(update, context):
    bot = context.bot
    user = update.effective_user
    
    keyboard = {
        "keyboard" : [
            ["🤩", "🙁"],
            ["/heute"]
        ],
        "resize_keyboard" : True
    }
    keyboard_str = dumps(keyboard)

    if "active_users" not in context.bot_data:
        context.bot_data["active_users"] = []

    if user in context.bot_data["active_users"]:
        bot.send_message(chat_id=user.id, text="Du bist schon in die Benutzer-Liste eingetragen.", reply_markup=keyboard_str)
    else:
        context.bot_data["active_users"].append(user)
        context.user_data["current_job"] = "Kleinscheiß"
        bot.send_message(chat_id=user.id, text="Hallo {}, ich habe dich zu meiner Benutzer-Liste hinzugefügt.".format(user.first_name), reply_markup=keyboard_str)
        # TODO: Menü schicken

    conn = sqlite3.connect("sql_data.db")
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS stars (id integer primary key autoincrement, user_name text, _date text, job text, stars integer);")

    conn.commit()
    conn.close()

# def reset_day():

def count_emojis(text):
    counter = 0
    for char in text:
        if char == "🤩":
            counter += 1
        if char == "🙁":
            counter -= 1
    return counter

def add_stars(user, amount, job):
    conn = sqlite3.connect("sql_data.db")
    c = conn.cursor()

    # Wurde der job heute schon einmal ausgeführt?
    results = c.execute("SELECT stars FROM stars WHERE _date=date('now') AND user_name=? AND job=?;", (user, job)).fetchone() # TODO: Funzt das?
    if results is None:
        # Job wurde noch nicht ausgeführt
        c.execute("INSERT INTO stars (user_name, _date, job, stars) VALUES (?,date('now'),?,?)",
            (user, job, amount))
        logging.info("Neuer Job für heute hinzugefügt.")
    else:
        # Job wurde heute schon einmal ausgeführt
        previous_amount = results[0]
        new_amount = previous_amount + amount
        c.execute("UPDATE stars SET stars=? WHERE _date=date('now') AND user_name=? AND job=?", (new_amount,user, job))
        logging.info("Job für heute aktualisiert.")


    conn.commit()
    conn.close()

def get_todays_stats(context):
    price = context.bot_data["price"]
    msg = "Heute geht es um den Preis: \"{}\". Bisher stehts:".format(price)
    for user in context.bot_data["active_users"]:
        msg += "\n\n{}:".format(user.first_name)

        conn = sqlite3.connect("sql_data.db")
        c = conn.cursor()

        results = c.execute("SELECT job, stars FROM stars WHERE user_name=? AND _date=date('now');", (user.first_name,)).fetchall()

        for result in results:
            msg += "\n{}: ".format(result[0])

            if result[1] > 0:
                for i in range(result[1]):
                    msg += "🤩"
            else:
                for i in range(abs(result[1])):
                    msg += "🙁"

        conn.commit()
        conn.close()

    return msg

def message(update, context):
    text = update.message.text
    split_txt = text.split(" ")

    if ("🤩" in split_txt[0] or "🙁" in split_txt[0]):
        # Nachricht mit Emojis am Anfang
        emojis = split_txt[0]

        if len(split_txt) > 1:
            # Nachricht fängt mit Emojis an, geht mit Text weiter
            job = " ".join(split_txt[1:])
            context.user_data["current_job"] = job
            msg = "Okay, du machst also gerade \"{}\".".format(job)
            context.bot.send_message(chat_id=update.effective_user.id, text=msg)

        stars = count_emojis(emojis)
        add_stars(update.effective_user.first_name, stars, context.user_data["current_job"])
        msg = "Ich habe dir {} Sternchen dafür hinzugefügt, dass du gerade \"{}\" machst.".format(stars, context.user_data["current_job"])
        context.bot.send_message(chat_id=update.effective_user.id, text=msg)

    elif "🤩" in split_txt[-1] or "🙁" in split_txt[-1]:
        # Nachricht mit Emojis am Ende
        emojis = split_txt[-1]

        if len(split_txt) > 1:
            # Nachricht fängt mit Text an, geht mit Emojis weiter
            job = " ".join(split_txt[:-1])
            context.user_data["current_job"] = job
            msg = "Okay, du machst also gerade \"{}\".".format(job)
            context.bot.send_message(chat_id=update.effective_user.id, text=msg)

        stars = count_emojis(emojis)
        add_stars(update.effective_user.first_name, stars, context.user_data["current_job"])
        msg = "Ich habe dir {} Sternchen dafür hinzugefügt, dass du gerade \"{}\" machst.".format(stars, context.user_data["current_job"])
        context.bot.send_message(chat_id=update.effective_user.id, text=msg)

    else:
        # Nachricht nur mit Text
        job = split_txt[0]
        context.user_data["current_job"] = job
        msg = "Okay, du machst also gerade \"{}\".".format(job)
        context.bot.send_message(chat_id=update.effective_user.id, text=msg)

def heute(update, context):
    context.bot.send_message(chat_id=update.effective_user.id, text=get_todays_stats(context))

def admin(update, context):
    context.bot_data.clear()
    context.user_data.clear()

def preis(update, context):
    if len(context.args) > 0:
        price = context.args[0]
        context.bot_data["price"] = price
        context.bot.send_message(chat_id=update.effective_user.id, text="Der neue Preis für heute ist also \"{}\"".format(price))
    else:
        context.bot.send_message(chat_id=update.effective_user.id, text="Du hast keinen Preis angegeben. Bitte gibt den Preis im Format: \"/preis Dein_Preis\" an.")


def main():
    logging.basicConfig(level=logging.INFO)

    token = "906705617:AAE4QgiX_7OSlyF5bFwKSof_-UUlF0C1OAs"

    bot = telegram.Bot(token=token)
    persistence = PicklePersistence(filename="persistent_bot_data")
    updater = Updater(token=token, persistence=persistence, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    heute_handler = CommandHandler("heute", heute)
    dispatcher.add_handler(heute_handler)

    preis_handler = CommandHandler("preis", preis)
    dispatcher.add_handler(preis_handler)

    # admin_handler = CommandHandler("admin", admin)
    # dispatcher.add_handler(admin_handler)

    message_handler = MessageHandler(Filters.text, message)
    dispatcher.add_handler(message_handler)

    logging.info("Waiting for updates...")
    updater.start_polling()
    updater.idle()



if __name__ == "__main__":
    main()