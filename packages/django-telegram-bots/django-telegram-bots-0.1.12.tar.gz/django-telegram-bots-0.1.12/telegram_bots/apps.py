# -*- coding: utf-8
from django.apps import AppConfig


class TelegramBotsConfig(AppConfig):
    name = 'telegram_bots'
    verbose_name = "TelegramBots"

    def ready(self):
        import telegram_bots.signals