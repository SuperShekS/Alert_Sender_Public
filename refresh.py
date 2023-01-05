"""Module to refresh at intervals."""

import time
import datetime as dt
from configparser import ConfigParser

config = ConfigParser()
FILE = 'config.ini'
config.read(FILE)

token_bot_4 = config['telegram']['bot_4']

admin_group = config['telegram']['group_3']

class Refresh:
    """Class for Activator."""
    def __init__(self) -> None:
        pass


    def repeat_refresher(self):
        """To repeatedly refresh the page at shorter intervals,
         and also check for new mails"""
        from activators import Activator
        activator_class = Activator()
        import wallet
        import mailer
        wallet_class = wallet.Wallet(wallet.global_holder['br'])
        mailer_class = mailer.Mailer(mailer.mail_dict['mail_login'])
        while True:
            wallet_class.still_logged_in('none')
            mailer_class.new_mail_checker()
            now = dt.datetime.now()
            # if now.isoweekday() < 6:
            slp = activator_class.sleep_timer(now, config['weekday'])
            starttime = time.time()
            if slp > 300:
                next_work_day = 3 if now.isoweekday() == 5 else 1
                day_temp = (dt.date.today().replace(day=28) + dt.timedelta(days=4) - dt.timedelta(days=(dt.date.today().replace(day=28) + dt.timedelta(days=4)).day)).day
                next_work_day_date = (now.day + next_work_day) - day_temp  if (now.day + next_work_day) > day_temp else (now.day + next_work_day)
                slp = (dt.datetime(now.year, now.month, next_work_day_date,  int(config['weekday']['start_time']))  - now).total_seconds()
                activator_class.send_message(('"refresher" going to sleep for ' + activator_class.sec_converter(slp)), token_bot_4, admin_group)
                time.sleep(slp - ((time.time() - starttime) % slp))
                activator_class.send_message(('"refresher" is up and running'), token_bot_4, admin_group)
                activator_class.send_message(('/init'), token_bot_4, admin_group)
                activator_class.send_message(('/start'), token_bot_4, admin_group)
            time.sleep(slp/2 - ((time.time() - starttime) % slp/2))


refresh = Refresh()
refresh.repeat_refresher()



