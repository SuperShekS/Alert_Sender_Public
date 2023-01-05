# Alert_Sender_Public
A project currently in pipeline, this is the public version. 


## Features

The code appears to involve a number of classes and functions for interacting with a wallet website and email account.
The code can perform the following actions:
Login to the wallet website and check balances (debit and credit)
Send alerts to a specified group on Telegram when certain conditions are met (e.g. low debit balance)
Check for new emails and send alerts on certain emails
Repeatedly refresh the wallet website and check for new emails at specified intervals
Provide a number of commands for interacting with the wallet and email functionality through Telegram (e.g. requesting balance updates)

## Requirements

The code uses the configparser, http, re, json, bs4, and mechanize libraries.
The code requires a config.ini file with certain defined fields (e.g. [telegram] section with bot_1, bot_2, bot_3, bot_4, group_1, group_3).
The code requires the activators.py and mailer.py files to be in the same directory.

## Usage

The code can be run by calling the refresh.repeat_refresher() function, which will start the refresh loop and wait for Telegram commands.
The available Telegram commands are:
/start: Welcome message and initialization of wallet and email logins
/help: List of available commands
/DebitBalance: Check debit balance
/CreditBalance: Check credit balance
/CheckAlert: Check for alerts
/GetDebitBalance: Get debit balance updates every 10 minutes
/GetCreditBalance: Get credit balance updates every 10 minutes


## OTHER ASPECTS

Other aspects of the project which is not shown, ML model whhich uses  
