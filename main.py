import Constants as keys
from telegram.ext import *
import logging
import csv
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove

print("Peete wacht auf")

EATING, GAME, PLAYING, START = range(4)
gespielt = False,
saved = False,

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start_command(update: Update, context: CallbackContext):
    print(update.message)
    #if not (saved):
    user = update.effective_user
    id = update.message.chat_id
    writecsv(id)
        #saved = True
    update.message.reply_text(
        f'Miau.. {user.first_name}. Ich bin Peete 😺 \n\nIch wurde das letzte mal um XX:XX Uhr von X.Name gefüttert.'
        f'\n\nHast du mich gefüttert?',
        reply_markup=ReplyKeyboardMarkup([["ja", "nein"]], one_time_keyboard=True, input_field_placeholder='Hast du mir was zu essen gemacht?'))
    return EATING


def eating(update, context):
    if update.message.text == "ja":
        sendMessageToAll(f'{update.effective_user.first_name} hat Peete gefüttert')
        futter = [["Makrele", "Gans", "Rind"], ["Lachsforelle", "Huhn"], ["Trockenfutter"], ["Sonstiges"]]
        update.message.reply_text("Womit hast du mich gefüttert?",
                                  reply_markup=ReplyKeyboardMarkup(
                                      futter,
                                      one_time_keyboard=False,
                                      input_field_placeholder="Womit hast du mich gefüttert?"))
        return PLAYING
    if update.message.text == "nein":
        update.message.reply_text("Bitte streichel mich trotzdem ❤")
        return START


def playing(update, context):
    food = update.message.text
    update.message.reply_text(
        "Hast du auch mit mir gespielt?",
        reply_markup=ReplyKeyboardMarkup(
            [["ja", "nein"]],
            one_time_keyboard=True,
            input_field_placeholder="Hast du auch mit mir gespielt?")
    )
    return GAME


def game(update, context):
    if update.message.text == "ja":
        sendMessageToAll()
        update.message.reply_text(
            "Wie lange?",
            reply_markup=ReplyKeyboardMarkup(
                [["5min", "10min", "15min"], ["20min", "25min", "30min"]]
            )
        )
        gespielt = True
    if update.message.text == "nein":
        update.message.reply_text("Okay schade")
        sendMessageToAll(f'{update.effective_user.first_name} hat Peete mit {} gefüttert.')


def writecsv(chatId):
    with open('usersChatIds.csv', 'a+', newline='') as write_obj:
        write_obj = csv.writer(write_obj)
        write_obj.writerow([chatId])


def sendMessageToAll(message):
    print("send Messages started...")
    # opening the CSV file
    with open('usersChatIds.csv', mode='r') as file:
        # reading the CSV file
        #csvFile = csv.reader(file)

        # displaying the contents of the CSV file
        for lines in file:
            send_text = f'https://api.telegram.org/bot{keys.API_KEY}/sendMessage?chat_id={lines}&parse_mode=Markdown&text={message}'

            response = requests.get(send_text)
            print(send_text)
            print(response)


def error(update, context):
    print(f"Update {update} caused error {context.error}")


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    updater = Updater(keys.API_KEY)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            EATING: [MessageHandler(Filters.text, eating), CommandHandler('start', start_command)],
            GAME: [MessageHandler(Filters.text, game), CommandHandler('start', start_command)],
            PLAYING: [MessageHandler(Filters.text, playing), CommandHandler('start', start_command)],
            START: [CommandHandler('start', start_command)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


main()
