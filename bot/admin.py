from django.contrib import admin
from .models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "external_id", "name", "level")


@admin.register(MessageText)
class MessageTextAdmin(admin.ModelAdmin):
    list_display = ("id", "message")


@admin.register(MenuText)
class MenuTextAdmin(admin.ModelAdmin):
    list_display = ("id", "button")


@admin.register(Category)
class CategoryTextAdmin(admin.ModelAdmin):
    list_display = ("id", "text")


@admin.register(Product)
class ProductTextAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "сat", "price1", "price2", "price3", "price4", "price5", "img")


class FilesUserAdmin(admin.TabularInline):
    model = FileOrder


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "step", "date_update", "date_create", "phone", "fio")
    inlines = [
        FilesUserAdmin,
    ]
    list_filter = [
        "step"
    ]
    search_fields = (
        "phone",
        "fio"
    )


admin.site.register(Order, OrderAdmin)
admin.site.register(FileOrder)
