
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
        bot.send_message(chat_id=user.id, text="Hallo {}, ich habe dich zu meiner Benutzer-Liste hinzugefügt.".format(user.first_name))
        # TODO: Menü schicken

def message(update, context):
    text = update.message.text

    if ("🤩" in text or "🙁" in text):
        # Message mit Text und Emoji

        # Einzelne Emoji

        # Message nur mit Emoji
        print("jo")
    else:
        # Message nur mit Text

    


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