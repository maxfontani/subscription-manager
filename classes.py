from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class Client:

    def __init__(self, name, tel, email = None, level = 'New', last_active_date = datetime.today()):
        self.name = name
        self.tel = tel
        self.email = email
        self.level = level
        self.last_active_date = last_active_date.strftime('%d/%m/%Y')


class Subscription:

    def __init__(self, holder, date_issued = date.today().strftime('%d/%m/%Y'), date_ends = date.today(), sub_type = 1, status = 'ACTIVE', days_frozen = 0):
        self.holder = holder
        self.date_issued = date_issued
        self.sub_type = sub_type
        self.status = status
        self.days_frozen = days_frozen

        # Calculate the subscription's end date based on its type
        date_issued_obj = datetime.strptime(self.date_issued, '%d/%m/%Y')
        date_ends = date_issued_obj + relativedelta(months=+sub_type)
        self.date_ends = date_ends.strftime('%d/%m/%Y')
