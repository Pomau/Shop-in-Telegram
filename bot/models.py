from django.db import models


class Profile(models.Model):
    level_client = [
        (1, 'Не купил'),
        (2, 'Обычный клиент'),
        (3, 'Постоянный клиент'),
        (4, 'Оптовик 1'),
        (5, 'Оптовик 2'),
    ]
    external_id = models.PositiveIntegerField(verbose_name="ID пользователя")
    name = models.CharField(verbose_name="Ник пользователя", max_length=200)
    level = models.IntegerField("Уровень клиента", choices=level_client, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


class MessageText(models.Model):
    message = models.TextField(verbose_name="Сообщение")

    class Meta:
        verbose_name = "Сообщения бота"
        verbose_name_plural = "Сообщения бота"


class MenuText(models.Model):
    button = models.TextField(verbose_name="Кнопка в меню")

    class Meta:
        verbose_name = "Кнопки в меню бота"
        verbose_name_plural = "Кнопки в меню бота"


class Category(models.Model):
    text = models.TextField(verbose_name="Категория")
    parent = models.ForeignKey('self', default=None, null=True, blank=True, related_name='nested_category',
                               on_delete=models.CASCADE, verbose_name="Родитель")
    nesting_level = models.IntegerField(default=1, verbose_name="Вложенный уровень")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Категории товаров"
        verbose_name_plural = "Категории товаров"


class Product(models.Model):
    name = models.CharField(verbose_name="Название", max_length=200)
    price1 = models.PositiveIntegerField(verbose_name="Цена для не купившего пользователя")
    price2 = models.PositiveIntegerField(verbose_name="Цена для обычнаго пользователя")
    price3 = models.PositiveIntegerField(verbose_name="Цена для постоянного клиента")
    price4 = models.PositiveIntegerField(verbose_name="Цена для оптовика 1")
    price5 = models.PositiveIntegerField(verbose_name="Цена для оптовика 2")
    text = models.TextField(verbose_name="Описание", null=True)
    img = models.ImageField(verbose_name="Изображение товара", null=True, upload_to='image/')
    description = models.TextField(verbose_name="Подробное описание (разделение на отдельные сообщения ';')", null=True,
                                   blank=True)
    ask = models.TextField(verbose_name="Вопросы к товару (разделение на отдельные сообщения ';')", null=True,
                           blank=True)
    data = models.TextField(verbose_name="Необходимые данные для покупки", null=True)
    сat = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        related_name="products"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товары"
        verbose_name_plural = "Товары"


class Order(models.Model):
    step_order = [
        (1, 'Клиент вводит данные'),
        (2, 'Не оплачен'),
        (3, 'Оплачен'),
        (4, 'Отправлен поставщику'),
        (5, 'Готов'),
        (6, 'Отменен'),
        (7, 'Отказ оператора')

    ]
    step = models.IntegerField("Статус заказа", choices=step_order)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="order"
    )
    data_kol = models.IntegerField(verbose_name="Количество загруженных данных", default=0)
    data_have = models.TextField(verbose_name="Введенные данные пользователем", default="", null=True)
    date_create = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    date_update = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)
    code = models.TextField(verbose_name="Код для платежа", default="", null=True)
    pay = models.IntegerField(verbose_name="Сумма", default=0)
    comment = models.TextField(verbose_name="Комментарий для пользователя", default="", null=True, blank=True)
    phone = models.CharField(verbose_name="Номер телефона", max_length=15, null=True)
    fio = models.CharField(verbose_name="ФИО", max_length=200, null=True)

    class Meta:
        verbose_name = "Заявка на покупку"
        verbose_name_plural = "Заявки на покупку"


class FileOrder(models.Model):
    file_order = models.FileField(verbose_name="Загружаемые данные", null=True, upload_to='documents/')
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True

    )

    class Meta:
        verbose_name = "Файлы"
        verbose_name_plural = "Файлы"
