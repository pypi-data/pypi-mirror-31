import telepot
import environ
import string
import random
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from easy_cache import ecached_property
from .utils import siging_auth

env = environ.Env()


@python_2_unicode_compatible
class Bot(models.Model):

    api_key = models.CharField(
        max_length=255,
        verbose_name=_('API Key'),
        unique=True
    )
    chat_id = models.CharField(
        max_length=255,
        verbose_name=_('Id')
    )
    first_name = models.CharField(
        max_length=255,
        verbose_name=_('First name')
    )
    username = models.CharField(
        max_length=255,
        verbose_name=_('Username')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Owner'),
        related_name='bots',
        on_delete=models.CASCADE
    )

    @property
    def get_me(self):
        data = self.bot.getMe()
        self.chat_id = data['id']
        self.first_name = data['first_name']
        self.username = data['username']
        return data

    @property
    def bot(self):
        return telepot.Bot(self.api_key)

    @property
    def active_auth_user_ids(self):
        return [user.id for user in self.authorizations.filter(is_active=True)]

    def send_message(self, chat_id, payload,
                     parse_mode=None, reply_markup=None):
        bot = self.bot
        message = bot.sendMessage(
            chat_id, payload, parse_mode=parse_mode, reply_markup=reply_markup)
        return message

    def save(self, *args, **kwargs):
        if not self.pk:
            self.get_me
            self.bot.setWebhook('https://{domain}/bots/{bot_token}/'.format(
                domain=env('DOMAIN_NAME', default='stagingserver.xyz'),
                bot_token=self.api_key
                )
            )
        return super(Bot, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.bot.deleteWebhook()
        return super(Bot, self).delete(*args, **kwargs)

    @ecached_property('bot_photos:{self.id}', timeout=3600)
    def photos(self):
        photos = []
        all_photos = self.bot.getUserProfilePhotos(self.chat_id)
        for photo_counter in range(all_photos['total_count']):
            for photo in all_photos['photos'][photo_counter]:
                if photo['height'] == 160:
                    file = self.bot.getFile(photo['file_id'])
                    path = 'https://api.telegram.org/file/bot{}/{}'.format(
                        self.api_key,
                        file['file_path']
                    )
                    photos.append(
                        {
                            photo['height']: path
                        }
                    )
        '''
        photos = defaultdict()
        all_photos = self.bot.getUserProfilePhotos(self.chat_id)
        for photo_counter in range(all_photos['total_count']):
            for photo in all_photos['photos'][photo_counter]:
                if not photo in photos:
                    print('hello'
                if not photo in photos:
                    photos[photo] = defaultdict()
                file = self.bot.getFile(photo['file_id'])
                path = 'https://api.telegram.org/file/bot{}/{}'.format(
                    self.api_key,
                    file['file_path']
                )
                photos[photo] = defaultdict({
                    photo['height']: path
                })
        '''
        return photos

    @ecached_property('bot_avatar:{self.id}', timeout=3600)
    def avatar(self):
        if self.photos:
            '''
            for photos in self.photos:
                for photo in self.photos[photos]:
                    return self.photos[photos][photo]
            '''
            return self.photos[-1][160]
        return None

    class Meta:
        verbose_name = _('Bot')
        verbose_name_plural = _('Bots')

    def __str__(self):
        return '%s' % str(self.first_name)

    def get_absolute_url(self):
        return reverse('telegram_bots_detail', kwargs={'pk': self.pk})


@python_2_unicode_compatible
class TelegramUser(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        verbose_name=_('User'),
        related_name='telegramuser',
        on_delete=models.CASCADE
    )
    token = models.CharField(
        max_length=255,
        verbose_name=_('Token')
    )
    chat_id = models.CharField(
        max_length=255,
        verbose_name=_('Chat id'),
        null=True,
        blank=False
    )

    def generate_token(self,
                       size=64,
                       chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
        return ''.join(random.choice(chars) for _ in range(size))

    def set_token(self):
        self.token = self.generate_token()

    def check_token(self, token):
        return self.token == token

    def save(self, *args, **kwargs):
        if not self.pk or not self.token:
            self.set_token()
        return super(TelegramUser, self).save(*args, **kwargs)

    def __str__(self):
        return '%s' % str(self.user.username)


@python_2_unicode_compatible
class Authorization(models.Model):

    bot = models.ForeignKey(
        Bot,
        on_delete=models.CASCADE,
        verbose_name=_('Bot'),
        related_name='authorizations'
    )
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='authorizations'
    )
    is_active = models.BooleanField(default=False, verbose_name=_('Is active'))

    @property
    def activation_url(self):
        signature = siging_auth(
            self.bot.username, self.user.user.username, self.pk
        )
        return reverse(
            'telegram_bots_subscribe', kwargs={'signature': signature}
        )

    @property
    def deactivation_url(self):
        signature = siging_auth(
            self.bot.username, self.user.user.username, self.pk
        )
        return reverse(
            'telegram_bots_unsubscribe', kwargs={'signature': signature}
        )

    class Meta:
        unique_together = (('bot', 'user'),)
