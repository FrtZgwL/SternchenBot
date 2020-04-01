
import telegram
from telegram.ext import Updater
from telegram.ext import Dispatcher
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import PicklePersistence
import sqlite3
import logging



def start(update, context):
    bot = context.bot
    user = update.effective_user
    
    if "active_users" not in context.bot_data:
        context.bot_data["active_users"] = []

    if user in context.bot_data["active_users"]:
        bot.send_message(chat_id=user.id, text="Du bist schon in die Benutzer-Liste eingetragen.")
    else:
        context.bot_data["active_users"].append(user)
        context.user_data["current_job"] = "Kleinscheiß"
        bot.send_message(chat_id=user.id, text="Hallo {}, ich habe dich zu meiner Benutzer-Liste hinzugefügt.".format(user.first_name))
        # TODO: Menü schicken

# def reset_day():

def count_emojis(text):
    counter = 0
    for char in text:
        if char == "🤩":
            counter += 1
        if char == "🙁":
            counter -= 1
    return counter

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
        msg = "Ich habe dir {} Sternchen dafür hinzugefügt, dass du gerade \"{}\" machst.".format(stars, context.user_data["current_job"])
        context.bot.send_message(chat_id=update.effective_user.id, text=msg)

    else:
        # Nachricht nur mit Text
        job = split_txt[0]
        context.user_data["current_job"] = job
        msg = "Okay, du machst also gerade \"{}\".".format(job)
        context.bot.send_message(chat_id=update.effective_user.id, text=msg)

    


# Befehl, um sich aus dem Bot austragen zu lassen

def main():
    logging.basicConfig(level=logging.INFO)

    token = "906705617:AAE4QgiX_7OSlyF5bFwKSof_-UUlF0C1OAs"

    bot = telegram.Bot(token=token)
    persistence = PicklePersistence(filename="persistent_bot_data")
    updater = Updater(token=token, persistence=persistence, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    message_handler = MessageHandler(Filters.text, message)
    dispatcher.add_handler(message_handler)

    logging.info("Waiting for updates...")
    updater.start_polling()
    updater.idle()



if __name__ == "__main__":
    main()