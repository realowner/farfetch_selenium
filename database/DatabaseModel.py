from peewee import *
import datetime

# database = SqliteDatabase('orders.db')
database = SqliteDatabase('orders.db')


class BaseModel(Model):
    class Meta:
        database = database


class OrdersModel(BaseModel):
    id = PrimaryKeyField(null=False)
    email = CharField(max_length=255, null=True)
    password = CharField(max_length=255, null=True)
    country = CharField(max_length=255, null=True)
    countryCode = CharField(max_length=255, null=True)
    # zipCode = CharField(max_length=255, null=True)
    phone = CharField(max_length=255, null=True)
    # orderPrices = CharField(max_length=255, null=True)
    orders = CharField(max_length=255, null=True)
    cards = CharField(max_length=255, null=True)
    add_date = DateField(null=True)
    date_of_check = DateField(null=True)
    status = CharField(max_length=255, null=True)
    created_at = IntegerField(null=True)
    updated_at = IntegerField(null=True)


    @staticmethod
    def get_by_email(email: str):
        # достаем нужную строку
        row = OrdersModel.get(OrdersModel.email == email)

        return row


    def set_phone(self, phone):
        try:
            self.phone = phone
            self.save()
            res = 'phone: row updated'
        except:
            res = 'phone: update fail'

        return res


    def set_country(self, country, countryCode):
        try:
            self.country = country
            self.countryCode = countryCode
            self.save()
            res = 'country: row updated'
        except:
            res = 'country: update fail'

        return res


    def set_orders(self, orders_count):
        try:
            self.orders = orders_count
            self.save()
            res = 'orders: row updated'
        except:
            res = 'orders: update fail'

        return res


    def set_status(self, status):
        try:
            self.status = status
            self.date_of_check = datetime.date.today().strftime('%d.%m.%Y')
            self.save()
            res = f'set status {status}!'
        except:
            res = 'status update fail'

        return res


    class Meta:
        db_table = "orders"
        order_by = ('id',)


class ProxyModel(BaseModel):
    id = PrimaryKeyField(null=False)
    host = CharField(max_length=255, null=True)
    port = CharField(max_length=255, null=True)
    login = CharField(max_length=255, null=True)
    password = CharField(max_length=255, null=True)
    status = CharField(max_length=255, null=True)
    created_at = IntegerField(null=False)
    updated_at = IntegerField(null=False)


    class Meta:
        db_table = 'proxy'
        order_by = ('id',)