import os
import random

import requests
from telegram.utils.request import Request
import string

from django.core.management.base import BaseCommand
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import CallbackContext, Updater, MessageHandler, Filters, CallbackQueryHandler

from bot.models import *
from tl_shop import settings




def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e

    return inner


# Проверка платежа qiwi
def payment_history_last(pk):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + settings.Token
    parameters = {'rows': 50}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + settings.Phone + '/payments', params=parameters).json()
    order = Order.objects.get(pk=pk)
    res = "NO"
    if order.step == 2:
        for transition in h["data"]:
            if order.pay == transition["sum"]["amount"] and order.code == transition["comment"]:
                res = "OK"
                order.step = 3
                order.save()
    return res


# Генератор названия файлов
def generate_name():
    length = 10
    letters = string.ascii_letters + string.digits
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


# Получить сообщение или создать
def get_mess(pk, text):
    message, _ = MessageText.objects.get_or_create(pk=pk, defaults={"message": text})
    return message.message


# Получить кнопку меню или создать
def get_menu(pk, text):
    menu, _ = MenuText.objects.get_or_create(pk=pk, defaults={"button": text})
    return menu.button


# Получить пользователя или создать
def get_person(chat_id, name=""):
    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': name,
            'level': 1
        }
    )
    return p


# Создание меню кнопок
def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu.json


# Собирает необходимую информацию
def zparse_data(p, data):
    order = p.order.filter(step__in=[1])[0]
    product = order.product
    kol_enter = order.data_kol + 1
    order.data_kol = kol_enter
    order.data_have = order.data_have + data + "\n"
    order.save()

    message_text = reply_markup = ""
    if len(product.data.split("\n")) == kol_enter:
        # Все необходимые данные введены
        order.step = 2
        order.code = ''.join(random.choice("0123456789") for i in range(9))
        order.save()
        message_text = get_mess(8, """🔥Для автоматического пополнения баланса переведите необходимую сумму одним платежом на этот QIWI кошелек: 

https://qiwi.com/p/{phone}

со следующим комментарием к переводу
{code}
⛔️Очень важно оставить код в комментарии, иначе платеж не будет засчитан!
️После отправки нажмите кпопку проверить платеж""").format(phone=settings.Phone, code=order.code)
        keyboard = [[InlineKeyboardButton(get_menu(8, "Проверить платеж"), callback_data='check-' + str(order.pk))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        # Если это телефон или ФИО, то записываем в заказ
        if kol_enter == 1:
            order.fio = data
            order.save()
        elif kol_enter == 2:
            order.phone = data
            order.save()
        message_text = get_mess(5, "Пожалуйства отправьте/введите {data}").format(
            data=product.data.split("\n")[kol_enter])
    return (message_text, reply_markup)


# Обработчик сообщений
@log_errors
def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    p = get_person(chat_id, update.message.from_user.username)
    message_text = get_mess(7, "Мы вас не поняли")
    reply_markup = ""

    if text == "/start" or text == "Отменить покупку":
        if text == "Отменить покупку" and p.order.filter(step__in=[1]).count() > 0:
            # Отменяем заказ
            order = p.order.filter(step__in=[1])[0]
            order.step = 6
            order.save()
            update.message.reply_text(text=get_mess(6, "Покупка отменена"))
        # Старт
        message_text = get_mess(1, "👋 Добрый день! выберите пункт меню")
        reply_markup = ReplyKeyboardMarkup([
            [get_menu(1, "📋 Тарифы")],
            [get_menu(2, "📝 Отзывы"), get_menu(3, "⭐️ Партнерская программа")],
            [get_menu(4, "⚙️ Поддержка")]
        ])
    elif MenuText.objects.filter(button=text).count() != 0:
        button = MenuText.objects.filter(button=text)[0]
        if button.pk == 1:
            message_text = get_mess(2, "Выберите тариф из списка")
            keyboard = [[InlineKeyboardButton(cat.text, callback_data='cat-' + str(cat.pk))] for cat in
                        Category.objects.filter(nesting_level=1)]
            reply_markup = InlineKeyboardMarkup(keyboard)
        elif button.pk == 2:
            message_text = get_mess(11, "Отзывы о нас:")
        elif button.pk == 3:
            message_text = get_mess(12, "Временно не доступен")
        elif button.pk == 4:
            message_text = get_mess(13, "По всем вопросам пишите админу: ")
    elif p.order.filter(step__in=[1]).count() != 0:
        # Загружаем введенные данные
        message_text, reply_markup = parse_data(p, text)

    if type(reply_markup) == str:
        update.message.reply_text(
            text=message_text
        )
    else:
        update.message.reply_text(
            text=message_text,
            reply_markup=reply_markup
        )


# Обработчик файлов
@log_errors
def message_files(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    # Качаем файл
    if update.message.document is None:
        file_id = update.message.photo[-1].file_id
        file_ras = "jpg"
    else:
        file_id = update.message.document.file_id
        file_ras = update.message.document.file_name.split('.')[-1]
    new_file = context.bot.get_file(file_id)
    path = os.path.join(settings.MEDIA_ROOT, 'documents') + "/"
    name = str(generate_name()) + "." + file_ras
    new_file.download(path + name)

    # Привязываем файл к модели
    file_ord = FileOrder()
    file_ord.file_order.name = "documents/" + name
    file_ord.save()

    p = get_person(chat_id, update.message.from_user.username)
    message_text = get_mess(7, "Мы вас не поняли")
    reply_markup = ""
    if p.order.filter(step__in=[1]).count() != 0:
        # Загружаем введенные данные
        file_ord.order = p.order.filter(step__in=[1])[0]
        file_ord.save()
        message_text, reply_markup = parse_data(p, settings.DOMAIN + file_ord.file_order.url)

    if type(reply_markup) == str:
        update.message.reply_text(
            text=message_text
        )
    else:
        update.message.reply_text(
            text=message_text,
            reply_markup=reply_markup
        )


# Обработчик Inline кнопок
@log_errors
def button(update: Update, context: CallbackContext):
    chat_id = context._chat_id_and_data[0]
    query = update.callback_query
    # Получить пользователя
    p = get_person(chat_id)

    variant = query.data.split("-")
    message_text = reply_markup = ""
    # Отменяем покупку, если пользователь нажал на inline кнопку
    if p.order.filter(step__in=[1]).count() != 0:
        order = p.order.filter(step__in=[1])[0]
        order.step = 6
        order.save()
        update.message.reply_text(text=get_mess(6, "Покупка отменена"))
    if variant[0] == "cat":
        # Обрабатываем нажатие на категорию
        cat = Category.objects.get(pk=int(variant[1]))
        if (cat.nested_category.count() > 0):
            message_text = get_mess(2, "Выберите тариф из списка")
            keyboard = [[InlineKeyboardButton(cat.text, callback_data='cat-' + str(cat.pk))] for cat in
                        cat.nested_category.all()]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            message_text = get_mess(3, "Выберите товар из списка")
            keyboard = [[InlineKeyboardButton(product.name, callback_data='product-' + str(product.pk))] for product in
                        cat.products.all()]
            reply_markup = InlineKeyboardMarkup(keyboard)
    elif variant[0] == "product":
        # Обрабатываем нажатие на товар
        product = Product.objects.get(pk=int(variant[1]))

        # Отправка фото и описания
        context.bot.send_photo(chat_id=chat_id, photo=open(product.img.path, 'rb'))
        context.bot.sendMessage(chat_id=chat_id, text=product.text)
        # Задаем вопросы
        if product.ask != "":
            message_text = product.ask.split(";")[0]
            keyboard = [
                [InlineKeyboardButton("Да", callback_data='yes-' + str(product.pk) + "-" + "0"),
                 InlineKeyboardButton("Нет", callback_data='no-' + str(product.pk) + "0")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            # Вызываем цену
            price_list = [product.price1, product.price2, product.price3, product.price4, product.price5]
            message_text = get_mess(4, "К оплате: {price} руб.").format(price=price_list[p.level - 1])
            keyboard = [[InlineKeyboardButton(get_menu(6, "Купить"), callback_data='buy-' + str(product.pk))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
    elif variant[0] == "buy":
        # Обрабатываем нажатие на кнопку купить
        product = Product.objects.get(pk=int(variant[1]))
        price_list = [product.price1, product.price2, product.price3, product.price4, product.price5]
        order = Order(step=1, product=product, user=p, pay=price_list[p.level - 1])
        order.save()

        # Отправляем доп. информацию
        description = product.description.split(";")
        for message in description:
            if message != "":
                context.bot.sendMessage(chat_id=chat_id, text=message)
        # Просим ввести необходимые данные
        message_text = get_mess(5, "Пожалуйства отправьте/введите {data}").format(data=product.data.split("\n")[0])
        reply_markup = ReplyKeyboardMarkup([
            [get_menu(7, "Отменить покупку")]
        ])
    elif variant[0] == "check":
        # Проверка платежа
        res = payment_history_last(variant[1])
        reply_markup = ReplyKeyboardMarkup([
            [get_menu(1, "📋 Тарифы")],
            [get_menu(2, "📝 Отзывы"), get_menu(3, "⭐️ Партнерская программа")],
            [get_menu(4, "⚙️ Поддержка")]
        ])
        if res == "OK":
            message_text = get_mess(9, "Оплата прошла успешно")
        else:
            message_text = get_mess(10, "Оплата пока не пришла")
    elif variant[0] == "yes":
        product = Product.objects.get(pk=int(variant[1]))
        if int(variant[2]) + 1 == len(product.ask.split(";")):
            # Вызываем цену
            price_list = [product.price1, product.price2, product.price3, product.price4, product.price5]
            message_text = get_mess(4, "К оплате: {price} руб.").format(price=price_list[p.level - 1])
            keyboard = [[InlineKeyboardButton(get_menu(6, "Купить"), callback_data='buy-' + str(product.pk))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            message_text = product.ask.split(";")[int(variant[2]) + 1]
            keyboard = [
                [InlineKeyboardButton("Да", callback_data='yes-' + str(product.pk) + "-" + str(int(variant[2]) + 1)),
                 InlineKeyboardButton("Нет", callback_data='no-' + str(product.pk) + "0")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
    elif variant[0] == "no":
        message_text = get_mess(14, "К сожалению вы не сможете заказать этот товар")
    # query.answer()
    if type(reply_markup) == str:
        if message_text != "":
            context.bot.sendMessage(chat_id=chat_id, text=message_text)
        # query.edit_message_text(
        #     text=message_text
        # )
    else:
        context.bot.sendMessage(chat_id=chat_id, text=message_text, reply_markup=reply_markup)
        # query.edit_message_text(
        #     text=message_text,
        #     reply_markup=reply_markup
        # )


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        # подключение
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=settings.TOKEN,
        )
        print(bot.get_me())

        # обработчики
        updater = Updater(
            bot=bot,
            use_context=True,
        )

        message_handler = MessageHandler(Filters.text, do_echo)
        media_handler = MessageHandler(Filters.document, message_files)
        photo_handler = MessageHandler(Filters.photo, message_files)
        updater.dispatcher.add_handler(message_handler)
        updater.dispatcher.add_handler(media_handler)
        updater.dispatcher.add_handler(photo_handler)

        updater.dispatcher.add_handler(CallbackQueryHandler(button))
        # запустить бесконечную обработку входящих сообщений
        updater.start_polling()
        updater.idle()
