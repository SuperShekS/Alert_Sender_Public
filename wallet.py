"""Module handling data from the user wallet."""

from configparser import ConfigParser
import http
import re
import json
from bs4 import BeautifulSoup
import mechanize


zero_bal = 0
old_credit_bal = 0

global_holder = {}
global_holder['mail_login'] = None
global_holder['old_credit_bal_real'] = 0

cookielib = http.cookiejar
cj = cookielib.CookieJar()
global_holder['br'] = mechanize.Browser()
global_holder['soup'] = 0


config = ConfigParser()
FILE = 'config.ini'
config.read(FILE)

web_username = config['wallet_details']['user']
web_pass    =  config['wallet_details']['passwd']

token_bot_3 = config['telegram']['bot_3']
token_bot_4 = config['telegram']['bot_4']

managers_group = config['telegram']['group_1']
admin_group = config['telegram']['group_3']

login = config['wallet']['login']
dashboard = config['wallet']['dashboard']
logout = config['wallet']['logout']


def _login(user = web_username, passw = web_pass):
    """Login command for wallet."""
    global_holder['br'].open(login)
    global_holder['br'].select_form(nr=0)
    global_holder['br'].form['UserName'] = user
    global_holder['br'].form['Password'] = passw
    global_holder['br'].submit()
    global_holder['soup'] = BeautifulSoup(global_holder['br'].open(dashboard), 'html.parser')
    return global_holder['br']


class Wallet:
    """Class for Wallet."""
    def __init__(self, _br) -> None:
        self._br = _br
        self.soup = global_holder['soup']
        

    def still_logged_in(self, task = 'none'):
        """Check if wallet is still logged in."""
        if self._br is None:
            self._br = _login()
            self.still_logged_in(task = task)
        self.refresher(task)
        if (len(self.soup.find_all("div", {"class": "login-header blue"}))  < 1) is False:
            self._br = _login()
            self.still_logged_in(task = task)
        debit_bal = self.debit_bal_checker()
        self.alert_credit(debit_bal, float(list(self.reader().keys())[-1]), zero_bal)
        if task == 'none':
            return
        return (self.credit_bal_checker()) if task == 'Credit_check' else (self.debit_bal_checker()) if task == 'Debit_check' else None


    def debit_bal_checker(self):
        """Check debit balance."""
        try:
            return (self.soup.find_all('span')[4].text.strip("()"))
        except IndexError as err:
            from activators import Activator
            activator_class = Activator()
            activator_class.send_message((repr(err) + '@ Check Debit balance'), token_bot_4, admin_group)


    def credit_bal_checker(self):
        """Check credit balance."""
        try:
            credit_index = self.soup.find_all("div", {"class": "value"})[2]
            credit_index = float(re.findall(r"[-+]?(?:\d*\.\d+|\d+)", (re.sub(' {2,}', ' ',credit_index.text.replace(",",''))))[0])
            if credit_index <= 100000 :
                credit_dict = {}
                credit_dict[0] = ['', 0]
                self.writer(credit_dict)
            return ("{:,.2f}".format(credit_index))
        except IndexError as err:
            from activators import Activator
            activator_class = Activator()
            activator_class.send_message((repr(err) + '@ Check Credit balance'), token_bot_4, admin_group)


    def writer(self, credit_dict):
        """Writes dictionary to disk."""
        with open("credit_dict.json", "w", encoding = 'utf8') as outfile:
            json.dump(credit_dict, outfile)

    def reader(self):
        """Reads dictionary from disk."""
        with open('credit_dict.json', 'r', encoding = 'utf8') as openfile:
            return json.load(openfile)

    def alert_credit(self, debit_bal, old_cred_bal = old_credit_bal, zero = zero_bal):
        """Alert for new credit."""
        from activators import Activator
        activator_class = Activator()
        try:
            if old_cred_bal >= zero:
                new_credit_bal = float(self.credit_bal_checker().replace(',',''))
                credit_dict = self.reader()
                if new_credit_bal > old_cred_bal and (new_credit_bal - old_cred_bal - float(credit_dict[list(credit_dict.keys())[-1]][1])) > 200000:
                    if new_credit_bal not in credit_dict.keys():
                        credit_dict[new_credit_bal] = ['', 0]
                    for amt in credit_dict.keys():
                        if credit_dict[amt][0] != 'Sent' and float(amt) > 200000:
                            activator_class.send_message('Credit advice: ' + "{:,.2f}".format(float(amt) - old_cred_bal - float(credit_dict[list(credit_dict.keys())[-2]][1]))
                                    + ' has been credited to your account \n' +  'Total balance ' + debit_bal, token_bot_3 ,  managers_group)
                            credit_dict[amt][0] = 'Sent'
                    self.writer(credit_dict)
                else :
                    amt = (list(credit_dict.keys())[-1])
                    credit_dict[amt][1] = (new_credit_bal - float(amt))
                    self.writer(credit_dict)

        except (IndexError, AttributeError) as err:
            activator_class.send_message((repr(err) + '@ Check Alert'), token_bot_4, admin_group)


    def refresher(self, task):
        """Refresh the webpages and returns the soup of the page."""
        ht_doc = self._br.open(dashboard)
        self.soup = BeautifulSoup(ht_doc, 'html.parser')
        if (len(self.soup.find_all("div", {"class": "login-header blue"}))  < 1) is False:
            self._br = _login()
            self.still_logged_in(task = task)
        self.alert_credit(self.debit_bal_checker(), float(list(self.reader().keys())[-1]), zero_bal)


    def signout(self):
        """Log out of wallet."""
        self._br.open(logout)


