from peewee import *

# database = SqliteDatabase('orders.db')
database = SqliteDatabase('test_orders.db')


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

    def update_with_status(self, country=None, countryCode=None, zipCode=None, phone=None, orderPrices=None,
                            status=None, orders=None, cards=None, date_of_check=None):
        # достаем нужную строку
        # row = OrdersModel.get(OrdersModel.id == id)
        # обновляем ее поля
        self.country = country
        self.countryCode = countryCode
        self.zipCode = zipCode
        self.phone = phone
        self.orderPrices = orderPrices
        self.status = status
        self.orders = orders
        self.cards = cards
        self.date_of_check = date_of_check
        # сохраняем 
        self.save()

    @staticmethod
    def get_by_email(email: str):
        # достаем нужную строку
        row = OrdersModel.get(OrdersModel.email == email)

        return row

    def set_country(self, address_book):
        pass

    def set_status(self, status):
        self.status = status
        self.save()


    class Meta:
        db_table = "orders"
        order_by = ('id',)
