import requests
import blockcypher
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core import signing
from django.utils.functional import cached_property
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from model_utils.models import TimeStampedModel, SoftDeletableModel
from django.core.validators import MinValueValidator
from django.contrib.postgres.fields import ArrayField
from . import api

domain = settings.DOMAIN_NAME
api_key = settings.BLOCKCYPHER_API_KEY

from gm2m import GM2MField

@python_2_unicode_compatible
class BaseWallet(TimeStampedModel, SoftDeletableModel):

    private = models.CharField(max_length=150, unique=True)
    public = models.CharField(max_length=150, unique=True)
    address = models.CharField(max_length=150, unique=True)
    wif = models.CharField(max_length=150, unique=True)

    #received_invoices = GenericRelation('wallets.Invoice', related_query_name='received_invoices')
    #sended_invoices = GenericRelation('wallets.Invoice')
    sended_invoices = GenericRelation(
        'wallets.Invoice',
        content_type_field='sender_wallet_type',
        object_id_field='sender_wallet_id',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return '({}) {}'.format(
            self.coin_symbol.upper(), 
            self.address
            )

    def get_absolute_url(self):
        return reverse('wallets:detail', kwargs={'wallet': self.coin_symbol, 'address': self.address})

    def spend(self, addresses, amounts):
        new_transaction = api.not_simple_spend(
            from_privkey=self.private,
            to_addresses=addresses,
            to_satoshis=amounts, 
            coin_symbol=self.coin_symbol,
            api_key=settings.BLOCKCYPHER_API_KEY
        )
        return new_transaction

    def spend_with_webhook(self, addresses, amounts):
        new_transaction = api.not_simple_spend(
            from_privkey=self.private,
            to_address=addresses,
            to_satoshis=amounts, 
            coin_symbol=self.coin_symbol,
            api_key=settings.BLOCKCYPHER_API_KEY
        )        
        self.set_webhook(to_addresses=addresses, transaction=new_transaction, event='confirmed-tx')
        return new_transaction

    def set_webhook(self, to_addresses, transaction, payload = None, event = 'confirmed-tx'):
        if payload:
            payload = signature.dumps(payload)
        signature = signing.dumps({
            'from_address': self.address,
            'to_addresses': to_addresses,
            'symbol': self.coin_symbol,
            'event': event,
            'transaction_id': transaction,
            'payload': payload
            })
        webhook = blockcypher.subscribe_to_address_webhook(
            callback_url='https://{}/wallets/webhook/{}/'.format(domain, signature),
            subscription_address=self.address,
            event=event,
            coin_symbol=self.coin_symbol,
            api_key=settings.BLOCKCYPHER_API_KEY
        )
        return webhook
    '''
    @property
    def rate(self):
        response = requests.get('https://api.coinmarketcap.com/v1/ticker/{}/'.format(self.coin_name))
        json_response = response.json()
        return json_response[0]['price_usd']
    '''

    @cached_property
    def address_details(self):
        return blockcypher.get_address_details(self.address, coin_symbol=self.coin_symbol)

    @cached_property
    def overview(self):
        return blockcypher.get_address_overview(self.address, coin_symbol=self.coin_symbol)

    @cached_property
    def balance(self):
        overview = blockcypher.get_address_overview(self.address, coin_symbol=self.coin_symbol)
        return overview['balance']

    @cached_property
    def transactions(self):
        get_address_full = self.address_details
        return get_address_full['txrefs']

    @staticmethod
    def transaction_details(tx_ref, coin_symbol='btc'):
        return blockcypher.get_transaction_details(tx_ref, coin_symbol)

    def create_invoice(self, wallets, amounts):
        invoice = Invoice.objects.create(
            amount = amounts,
            sender_wallet_object = self
        )
        invoice.receiver_wallet_object = wallets
        invoice.save()
        
        return invoice

    @classmethod
    def get_coin_symbol(cls):
        for field in cls._meta.fields:
            if field.name == 'coin_symbol':
                return field.default

    @classmethod
    def get_coin_name(cls):
        for field in cls._meta.fields:
            if field.name == 'coin_name':
                return field.default

    @classmethod
    def get_rate(cls):
        coin_name = cls.get_coin_name()
        response = requests.get('https://api.coinmarketcap.com/v1/ticker/{}/'.format(coin_name))
        json_response = response.json()
        return json_response[0]['price_usd']


@python_2_unicode_compatible
class Btc(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="btc_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='btc')
    coin_name = models.CharField(max_length=10, default='bitcoin')

    @cached_property
    def total_balance(self):
        balance = 0
        for address in self.user.btc_wallets.all():
            balance += address.balance
        return balance


@python_2_unicode_compatible
class Doge(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="doge_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='doge')
    coin_name = models.CharField(max_length=10, default='dogecoin')

    @cached_property
    def total_balance(self):
        balance = 0
        for address in self.user.doge_wallets.all():
            balance += address.balance
        return balance


@python_2_unicode_compatible
class Ltc(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ltc_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='ltc')
    coin_name = models.CharField(max_length=10, default='litecoin')

    @cached_property
    def total_balance(self):
        balance = 0
        for address in self.user.ltc_wallets.all():
            balance += address.balance
        return balance


@python_2_unicode_compatible
class Dash(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="dash_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='dash')
    coin_name = models.CharField(max_length=10, default='dash')

    @cached_property
    def total_balance(self):
        balance = 0
        for address in self.user.dash_wallets.all():
            balance += address.balance
        return balance


@python_2_unicode_compatible
class Bcy(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bcy_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='bcy')
    coin_name = models.CharField(max_length=10, default='bcy')

    @property
    def rate(self):
        return 0

    @cached_property
    def total_balance(self):
        balance = 0
        for address in self.user.bcy_wallets.all():
            balance += address.balance
        return balance        


@python_2_unicode_compatible
class Invoice(models.Model):

    limit = models.Q(app_label='wallets', model='btc') | \
            models.Q(app_label='wallets', model='ltc') | \
            models.Q(app_label='wallets', model='dash') | \
            models.Q(app_label='wallets', model='doge') | \
            models.Q(app_label='wallets', model='bcy')

    #amount = models.BigIntegerField(validators=[MinValueValidator(0)])
    amount = ArrayField(
        models.BigIntegerField(validators=[MinValueValidator(0)]), blank=True
    )
    #receiver_wallet_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit, related_name='received_invoices')
    #receiver_wallet_id = models.PositiveIntegerField()
    #receiver_wallet_object = GenericForeignKey('receiver_wallet_type', 'receiver_wallet_id')

    sender_wallet_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit, related_name='sended_invoices')
    sender_wallet_id = models.PositiveIntegerField()
    sender_wallet_object = GenericForeignKey('sender_wallet_type', 'sender_wallet_id')

    receiver_wallet_object = GM2MField()

    is_paid = models.BooleanField(default=False)


    def __init__(self, *args, **kwargs):
        super(Invoice, self).__init__(*args, **kwargs)
        self.__tracked_fields = ['is_paid']
        self.set_original_values()

    def set_original_values(self):
        for field in self.__tracked_fields:
            if getattr(self, field) is 'True':
                setattr(self, '__original_%s' % field, True)
            elif getattr(self, field) is 'False':
                setattr(self, '__original_%s' % field, False)
            else:
                setattr(self, '__original_%s' % field, getattr(self, field))
        return self.__dict__

    def has_changed(self):
        for field in self.__tracked_fields:
            original = '__original_%s' % field
            return getattr(self, original) != getattr(self, field)

    def reset_original_values(self):
        values = {}
        for field in self.__tracked_fields:
            original = '__original_%s' % field
            setattr(self, field, getattr(self, original))
            values[field] = getattr(self, field)
        return values

    def pay(self):
        tx_ref = self.sender_wallet_object.spend_with_webhook(
            [wallet.address for wallet in self.receiver_wallet_object.all()],
            [amount for amount in self.amount]
            )
        invoice_transaction = InvoiceTransaction.objects.create(invoice = self, tx_ref = tx_ref)
        return invoice_transaction.tx_ref

    def get_absolute_url(self):
       return reverse('wallets:invoice_detail', kwargs={'pk': self.pk})
    
    def can_be_paid(self):
        if self.tx_refs.all():
            total_amount = 0
            tx_refs_total_amount = 0
            for tx in self.tx_refs.all():                                        
                details = blockcypher.get_transaction_details(
                    tx.tx_ref,
                    self.sender_wallet_object.coin_symbol
                )
                tx_refs_total_amount += details['outputs'][0]['value']
            assert int(sum(self.amount)) < tx_refs_total_amount, 'Invoice can be confirmed, because the amount of all transactions is less than the amount of the invoice.'
            return True
        return False
    
    def save(self, *args, **kwargs):
        self.full_clean()
        if self.has_changed():
            if not self.can_be_paid():
                self.reset_original_values()
        self.set_original_values()
        return super(Invoice, self).save(*args, **kwargs)


@python_2_unicode_compatible
class InvoiceTransaction(models.Model):

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='tx_refs')
    tx_ref = models.CharField(max_length=100, null=True, blank=False)

    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.tx_ref