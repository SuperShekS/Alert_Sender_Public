"""Module handling mails."""

from configparser import ConfigParser
import time
import imaplib
import json
import re
import datetime as dt
from collections import OrderedDict
from bs4 import BeautifulSoup


config = ConfigParser()
FILE = 'config.ini'
config.read(FILE)

mail_add  =  config['mail_details']['user']
mail_pass =  config['mail_details']['passwd']

mails = {}
msgs = {}


token_bot_3 = config['telegram']['bot_3']

cashiers_group = config['telegram']['group_2']

mail_dict = {}
mail_dict['mail_login'] = None

def login_mail(add = mail_add, passw = mail_pass):
    """Login for mail."""
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(add, passw)
        mail.list()
        mail.noop()
        mail_dict['mail_login'] = mail
        return mail
    except imaplib.IMAP4.error:
        print( "Log in error.")


def writer(obj_to_json, file_name):
    """Writes dictionary to disk."""
    with open(file_name + '.json', "w", encoding = 'utf8') as outfile:
        json.dump(obj_to_json, outfile)


def reader(json_to_obj):
    """Reads dictionary from disk."""
    with open(json_to_obj, 'r', encoding = 'utf8') as openfile:
        return json.load(openfile)

def nested_dict_pairs_iterator(dict_obj):
    ''' This function accepts a nested dictionary as argument
        and iterate over all values of nested dictionaries
    '''
    # Iterate over all key-value pairs of dict argument
    for key, value in dict_obj.items():
        # Check if value is of dict type
        if isinstance(value, dict):
            # If value is dict then iterate over all its values
            for pair in  nested_dict_pairs_iterator(value):
                yield (key, *pair)
        else:
            # If value is not dict type then yield the value
            yield (key, value)

users_dict = reader('users_dict.json')
users_gen = nested_dict_pairs_iterator(users_dict)

class Mailer:
    """Class for mail commands."""
    def __init__(self, mail) -> None:
        self.mail = mail
        self.users_gen = users_gen
        self.users_dict = users_dict


    def new_mail_checker(self):
        """Checks for new  mail from noop then calls transaction alert checker."""
        try:
            while True:
                if self.mail is None:
                    self.mail = login_mail()
                    self.new_mail_checker()
                self.mail.select("inbox")
                temp_search = self.mail_search()
                if temp_search is None:
                    break
                self.trans_getter(temp_search)
        except:
            self.mail = login_mail()
            self.new_mail_checker()


    def replace_all(self, text):
        """Removes unwanted symbols from text."""
        _od = OrderedDict([("=", ""),("\r", ""), ("\n", ""), ('C2A0', ''), ('NGN', '')])
        for i, j in _od.items():
            return text.replace(i, j)


    def msg_gen(self, tran):
        """Generates text to be sent to telegram."""
        keys = 'Staff', 'Transaction Type', 'Amount', 'Account Number', 'Narration', 'Time'
        msg = ''
        for key in keys:
            if key == 'Staff':
                msg += '-' * 35
                msg += '\n New alert for ' + str(tran[key]) + ' \n'
                msg += '-' * 35 + '\n\n'
            else:
                msg += key +' :         ' + str(tran[key]) + ' \n'
        msg += '_' * 30
        return msg


    def manager_mail_add_finder(self, soup):
        """Checks for the users email address."""
        for addr in re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", soup.decode("utf-8")):
            if addr[addr.index('@') + 1 : ] == 'gmail.com' and addr != 'gmail.com@gmail.com' and addr != 'chipsandcodes@gmail.com':
                return addr
            if addr[addr.index('@') + 1 : ] == 'yahoo.com':
                return addr
            if addr[addr.index('@') + 1 : ] == 'ymail.com':
                return addr


    def trans_getter(self, ids):
        """Gets the mail text with mail id, soup to get particular lines
        checks if the text meets the criteria and sends to telegram."""
        from activators import Activator
        activator_class = Activator()
        if mail_dict['mail_login'] is None:
            self.mail = login_mail()
            self.new_mail_checker()
        mail_dict['tran_msg'] = {}
        uba_ids, gtb_ids, zen_ids = ids
        if len(uba_ids) > 0:
            for _id in uba_ids:
                self.uba_get(_id)
        if len(gtb_ids) > 0:
            for _id in gtb_ids:
                self.gtb_get(_id)
        if len(zen_ids) > 0:
            for _id in zen_ids:
                self.zen_get(_id)
        print(mail_dict)
        for key in mail_dict['tran_msg'].keys():
            for user_info in self.users_gen:
                if user_info[3] == mail_dict['tran_msg'][key]['mail_add']:
                    company, manager, mail_type, manager_mail = user_info[0], user_info[1], user_info[2], user_info[3]
                    break
            temp_dict = self.users_dict[company][manager][mail_type][manager_mail]
            print(temp_dict)
            if mail_dict['tran_msg'][key]['Account Number'] in temp_dict['accounts'].keys() and float(mail_dict['tran_msg'][key]['Amount'].replace(',','')) < 210000 and float(mail_dict['tran_msg'][key]['Amount'].replace(',','')) > 500 :
                mail_dict['tran_msg'][key]['Staff'] = temp_dict['accounts'][mail_dict['tran_msg'][key]['Account Number']]
                activator_class.send_message(self.msg_gen(mail_dict['tran_msg'][key]), token_bot_3, temp_dict['group'])


    def gtb_get(self, _id):
        """Extract required information from GTB alerts."""
        raw_email = self.mail.fetch(_id, "(RFC822)")[1][0][1]
        soup = BeautifulSoup(raw_email, 'html.parser')
        table_res = soup.find_all('td')
        trans_table_res = table_res[14:35]
        for i in range(len(trans_table_res)-2, 0, -3):
            trans_table_res.pop(i)
        tran = {}
        int_id = int(_id.decode("utf-8"))
        mail_dict['tran_msg'][int_id] = {}
        mail_dict['tran_msg'][int_id]['mail_add'] = self.manager_mail_add_finder(soup)
        for i in range(0, len(trans_table_res), 2):
            tran[' '.join(self.replace_all(trans_table_res[i].text).split())]  = ' '.join(self.replace_all(trans_table_res[i + 1].text).split())
        mail_dict['tran_msg'][int_id]['Transaction Type'] = 'Credit'
        mail_dict['tran_msg'][int_id]['Amount'] = tran['Amount'].split()[-1]
        mail_dict['tran_msg'][int_id]['Account Number'] = tran['Account Number']
        mail_dict['tran_msg'][int_id]['Narration'] = tran['Description'] + ' || '+tran['Remarks']
        mail_dict['tran_msg'][int_id]['Time'] = tran['Time of Transaction']


    def zen_get(self, _id):
        """Extract required information from Zenith alerts."""
        raw_email = self.mail.fetch(_id, "(RFC822)")[1][0][1]
        soup = BeautifulSoup(raw_email, 'html.parser')
        table_res = soup.find_all('td')
        trans_table_res = table_res[7:29]
        tran = {}
        int_id = int(_id.decode("utf-8"))
        mail_dict['tran_msg'][int_id] = {}
        mail_dict['tran_msg'][int_id]['mail_add'] = self.manager_mail_add_finder(soup)
        for i in range(0, len(trans_table_res), 2):
            tran[' '.join(self.replace_all(trans_table_res[i].text).split())]  = ' '.join(self.replace_all(trans_table_res[i + 1].text).split())
        mail_dict['tran_msg'][int_id]['Transaction Type'] = tran['Transaction Type']
        mail_dict['tran_msg'][int_id]['Amount'] = tran['Amount']
        mail_dict['tran_msg'][int_id]['Account Number'] = tran['Account Number']
        mail_dict['tran_msg'][int_id]['Narration'] = tran['Description']
        mail_dict['tran_msg'][int_id]['Time'] = tran['Date of Transaction']


    def uba_get(self, _id):
        """Extract required information from UBA alerts."""
        raw_email = self.mail.fetch(_id, "(RFC822)")[1][0][1]
        soup = BeautifulSoup(raw_email, 'html.parser')
        table_res = soup.find_all('td')
        trans_table_res = table_res[3:23]
        tran = {}
        int_id = int(_id.decode("utf-8"))
        mail_dict['tran_msg'][int_id] = {}
        mail_dict['tran_msg'][int_id]['mail_add'] = self.manager_mail_add_finder(soup)
        for i in range(0, len(trans_table_res), 2):
            tran[' '.join(self.replace_all(trans_table_res[i].text).replace('\r', '').replace('\n', '').replace('=', '').split())]  = ' '.join(self.replace_all(trans_table_res[i + 1].text).split())
        mail_dict['tran_msg'][int_id]['Transaction Type'] = tran['Transaction Type']
        mail_dict['tran_msg'][int_id]['Amount'] = tran['Transaction Amount']
        mail_dict['tran_msg'][int_id]['Account Number'] = tran['Account Number']
        mail_dict['tran_msg'][int_id]['Narration'] = tran['Transaction Narration']
        mail_dict['tran_msg'][int_id]['Time'] = tran['Date and Time']


    def mail_search(self):
        """Search new mails with the search criterias and returns mail ids."""
        self.mail.select("inbox")
        uba_search = self.mail.search(None, '(FROM "UBA.Alert@ubagroup.com" SUBJECT "UBA CREDIT Transaction Notification")', "Unseen")[1][0].split()
        gtb_search = self.mail.search(None, '(FROM "GeNS@gtbank.com" SUBJECT "Gens Transaction Alert [CREDIT")', "Unseen")[1][0].split()
        zen_search = self.mail.search(None, '(FROM "ebusinessgroup@zenithbank.com" SUBJECT "Zenith Transaction Alert [CREDIT")', "Unseen")[1][0].split()
        search_list = [uba_search, gtb_search, zen_search]
        return search_list if sum(len(lists) for lists in search_list) > 0 else None


    def alert_finder(self):
        """Checks for 'new_mail_checker' but repeatedly for a few more minutes while also
        updating the customer."""
        from activators import Activator
        activator_class = Activator()
        try:
            if self.mail is None:
                self.mail = login_mail()
                self.alert_finder()

            self.mail.select("inbox")
            temp_search = self.mail_search()
            if temp_search is None:
                time.sleep(3)
                activator_class.send_message('No alert for now, we would keep check for a few minutes')  # need to define group or remove
                for i in range(40,121, 40):
                    finish_time = dt.datetime.now() + dt.timedelta(minutes = 4, seconds = 3)
                    if dt.datetime.now() < finish_time:
                        time.sleep(i)
                        self.mail.select("inbox")
                        temp_search = self.mail_search()
                        if temp_search is not None:
                            activator_class.send_message('Found something')          # need to define group or remove
                            self.trans_getter(temp_search)
                            activator_class.send_message('Done...')                  # need to define group or remove
                            return
                        if i < 90:
                            activator_class.send_message('Still checking...')
                activator_class.send_message('No alerts for now, check back later...')
                return

            activator_class.send_message('Found something')
            time.sleep(1)
            self.trans_getter(temp_search)
            activator_class.send_message('Done...')
        except:
            self.mail = login_mail()
            self.alert_finder()



 
# mailer_class = Mailer(mail_dict['mail_login'])
# mailer_class.new_mail_checker()