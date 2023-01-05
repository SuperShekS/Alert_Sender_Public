"""Module for functions that perform major actions."""

import time
import datetime as dt
from configparser import ConfigParser
import requests

config = ConfigParser()
FILE = 'config.ini'
config.read(FILE)

web_username = config['wallet_details']['user']
web_pass    =  config['wallet_details']['passwd']

token_bot_2 = config['telegram']['bot_2']
token_bot_3 = config['telegram']['bot_3']
token_bot_4 = config['telegram']['bot_4']

managers_group = config['telegram']['group_1']
cashiers_group = config['telegram']['group_2']
admin_group = config['telegram']['group_3']


class Activator:
    """Class for Activator."""
    def __init__(self) -> None:
        pass

    def send_message(self, msg, token = token_bot_3, _id = cashiers_group):
        """Sends message via telegram api directly to the groups (_id)."""
        telegram_api_url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id=@{_id}&text={msg}"
        requests.get(telegram_api_url)

    def repeater(self, amount, func):
        """Repeatedly checks either credit or debit balance and sends to cashier group every minute for 5 minutes."""
        for i in range(0,300, 60):
            finish_time = dt.datetime.now() + dt.timedelta(minutes = 5, seconds = 1)
            if dt.datetime.now() < finish_time:
                time.sleep(i)
                now = dt.datetime.now()
                inputs = ((now.hour + 1), now.minute, now.second, func, amount)
                msg = f"As at: {inputs[0]}:{inputs[1]}:{inputs[2]}, the {inputs[3]} balance is {inputs[4]}"
                self.send_message(msg)

    def compare(self, new_bal, old_bal):
        """Just a comparison function, nothing special."""
        return new_bal == old_bal


    def sleep_timer(self, now, schedule):
        """Sets the work time for the function, between the days of the week."""
        if int(schedule['end_time']) <= (now.hour + 1) and (now.hour + 1) >= int(schedule['start_time']):
            sleep_time = (dt.datetime(now.year, now.month, (now.day + 1),  int(schedule['start_time']))  - now).total_seconds()
        elif int(schedule['start_time']) <= (now.hour + 1) and 17> (now.hour + 1):
            sleep_time = (int(schedule['slp_morning']))
        elif 17 <= (now.hour + 1) and 19> (now.hour + 1):
            sleep_time = (int(schedule['slp_afternoon']))
        elif 19 <= (now.hour + 1) and int(schedule['end_time'])>= (now.hour + 1):
            sleep_time = (int(schedule['slp_night']))
        return sleep_time

    def sec_converter(self, seconds):
        """Converts seconds to days, hours and minutes."""        
        result = []
        intervals = (('weeks', 604800),('days', 86400),('hours', 3600),('minutes', 60),('seconds', 1))

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(int(value), name))
        return ', '.join(result[:3])

    def repeat_notifier(self):
        """Repeatedly checks debit balance all day and sends to manager groups if there is change
        in the balance and within the time constraints set. 23 secondss added in other to stagger 
        the refresh time in correspondence to that of refresh.py"""
        import wallet
        import mailer
        mailer_class = mailer.Mailer(mailer.mail_dict['mail_login'])
        wallet_class = wallet.Wallet(wallet.global_holder['br'])

        new_bal = 0
        self.send_message('The balances would be updated every 5 minutes', token_bot_2,  managers_group)
        while True:
            old_bal = new_bal
            temp_debit = wallet_class.still_logged_in('Debit_check')
            try:
                new_bal = float(temp_debit.replace(',',''))
                if self.compare(new_bal, old_bal) is False:                                              # change to False
                    self.send_message('Your available balance is ' + temp_debit,  token_bot_2, managers_group)
                mailer_class.new_mail_checker()
                now = dt.datetime.now()
                starttime = time.time()
                if now.isoweekday() < 6:
                    slp = self.sleep_timer(now, config['weekday'])
                elif now.isoweekday() == 6:
                    slp = self.sleep_timer(now, config['sat'])
                else:
                    slp = self.sleep_timer(now, config['sun'])
                if slp > 4000:
                    self.send_message(('"repeat_notifier" going to sleep for ' + self.sec_converter(slp)), token_bot_4, admin_group)
                time.sleep((slp + 23) - ((time.time() - starttime) % (slp + 23)))
            except AttributeError as err:
                self.send_message((repr(err) + '@ repeat_notifier'), token_bot_4, admin_group)

