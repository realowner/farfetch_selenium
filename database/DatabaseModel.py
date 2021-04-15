from peewee import *

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
    zipCode = CharField(max_length=255, null=True)
    phone = CharField(max_length=255, null=True)
    orderPrices = CharField(max_length=255, null=True)
    status = CharField(max_length=255, null=True)
    orders = CharField(max_length=255, null=True)
    cards = CharField(max_length=255, null=True)
    add_date = DateField(null=True)
    date_of_check = DateField(null=True)
    created_at = IntegerField(null=True)
    updated_at = IntegerField(null=True)

    def update_with_status_2(self, country=None, countryCode=None, zipCode=None, phone=None, orderPrices=None,
                             orders=None, cards=None, date_of_check=None):
        # достаем нужную строку
        # row = OrdersModel.get(OrdersModel.id == id)
        # обновляем ее поля
        self.country = country
        self.countryCode = countryCode
        self.zipCode = zipCode
        self.phone = phone
        self.orderPrices = orderPrices
        self.status = 2
        self.orders = orders
        self.cards = cards
        self.date_of_check = date_of_check
        # сохраняем 
        self.save()

    def update_with_status_3(id):
        # достаем нужную строку
        row = OrdersModel.get(OrdersModel.id == id)
        # обновляем ее поля
        row.status = 3
        # сохраняем 
        row.save()

    @staticmethod
    def get_by_email(email: str):
        # достаем нужную строку
        row = OrdersModel.get(OrdersModel.email == email)

        return row

    @staticmethod
    def get_by_status(status):
        # достаем нужную строку
        rows = OrdersModel.get(OrdersModel.status == status)

        return rows

    def set_country(self, address_book):
        adr = address_book.get('addressBook', {}).get('addresses', [])
        if adr:
            self.countryCode = adr[0]['flatAddress']['country']['alpha2Code']
            self.country = adr[0]['flatAddress']['country']['nativeName']
            self.phone = adr[0]['flatAddress'].get('phone', None)
            self.save()

    def set_status(self, status):
        self.status = status
        self.save()

    class Meta:
        db_table = "orders"
        order_by = ('id',)
