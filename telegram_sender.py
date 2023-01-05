"""Module handling telegram connection and calling other m."""

from configparser import ConfigParser
import time
from telegram.update import Update
from telegram.ext.updater import Updater
from telegram.ext.filters  import  Filters
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
import wallet
import mailer

from activators import Activator
activator_class = Activator()

wallet_class = wallet.Wallet(wallet.global_holder['br'])
mailer_class = mailer.Mailer(mailer.mail_dict['mail_login'])

config = ConfigParser()
FILE = 'config.ini'
config.read(FILE)

web_username = config['wallet_details']['user']
web_pass    =  config['wallet_details']['passwd']

token_bot_1 = config['telegram']['bot_1']
token_bot_2 = config['telegram']['bot_2']
token_bot_4 = config['telegram']['bot_4']

updater = Updater( token_bot_1, use_context=True)
updater_2 = Updater( token_bot_2, use_context=True)
updater_4 = Updater( token_bot_4, use_context=True)


def start(update: Update, context: CallbackContext):
    """Telegram command to start the program, initializes both the mail and wallet logins."""
    time.sleep(1)
    update.message.reply_text("Welcome to Shekoni Shekoni & Co. Telegram group!")
    wallet_class.still_logged_in(task = 'None')
    mailer_class.new_mail_checker()
    update.message.reply_text( "To get help press /help.")


def help(update: Update, context: CallbackContext):
    """ Telegram command for Help text on how to use."""
    time.sleep(1)
    update.message.reply_text("""Available Commands :- \n
       1) "/start for welcome message \n
       2) "/help for commands \n
       3) "/DebitBalance" To check balances\n 
       4) "/CreditBalance" To check balances\n 
       5) "/CheckAlert" To check for alerts\n 
       6) "/GetDebitBalance" to get debit balance updates in 10 mins\n
       7) "/GetCreditBalance" to get credit balance updates in 10 mins\n
""")


def creditbalance(update: Update, context: CallbackContext):
    """Telegram command to initialize a check on the credit balance."""
    cred = wallet_class.still_logged_in(task = 'Credit_check')
    time.sleep(1)
    update.message.reply_text( "Available credit: " + cred)


def debitbalance(update: Update, context: CallbackContext):
    """Telegram command to initialize a check on the debit balance."""
    time.sleep(1)
    deb = wallet_class.still_logged_in(task = 'Debit_check')
    update.message.reply_text("Available amount: " + deb)


def getdebitbalance(update: Update, context: CallbackContext):
    """Telegram command to initialize 'repeater' on the debit balance."""
    deb = wallet_class.still_logged_in(task = 'Debit_check')
    time.sleep(1)
    update.message.reply_text("Hold on a second, while we review the balances")
    time.sleep(2)
    update.message.reply_text("Current avaialable balance is " + deb)
    time.sleep(55)
    activator_class.repeater(wallet_class.still_logged_in(task = 'Debit_check'), "Debit")


def getcreditbalance(update: Update, context: CallbackContext):
    """Telegram command to initialize 'repeater' on the credit balance."""
    cred = wallet_class.still_logged_in(task = 'Credit_check')
    time.sleep(1)
    update.message.reply_text("Hold on a second, while we review the credit balances")
    time.sleep(2)
    update.message.reply_text("Current avaialable balance is " + cred)
    time.sleep(55)
    activator_class.repeater(wallet_class.still_logged_in(task = 'Credit_check'), "Credit")


def checkalert(update: Update, context: CallbackContext):
    """Telegram command to initialize 'alert_finder' on the mail."""
    time.sleep(1) 
    update.message.reply_text("Checking...")
    mailer_class.alert_finder()


def init(update: Update, context: CallbackContext):
    """A dummy docstring."""
    activator_class.repeat_notifier()


def stop(update: Update, context: CallbackContext):
    """Telegram command to sign out."""
    update.message.reply_text("Understood..")
    wallet_class.signout()
    time.sleep(2)
    update.message.reply_text("Done..")



updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('getdebitbalance', getdebitbalance))
updater.dispatcher.add_handler(CommandHandler('stop', stop))
updater.dispatcher.add_handler(CommandHandler('getcreditbalance', getcreditbalance))
updater.dispatcher.add_handler(CommandHandler('checkalert', checkalert))
updater_2.dispatcher.add_handler(CommandHandler('init', init))
updater_4.dispatcher.add_handler(CommandHandler('debitbalance', debitbalance))
updater_4.dispatcher.add_handler(CommandHandler('creditbalance', creditbalance))

updater.start_polling()
updater_2.start_polling()
updater_4.start_polling()
