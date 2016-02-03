# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.utils import timezone


class Business(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField(null=True, default=0)
    profit = models.FloatField(null=True, default=0)
    active = models.BooleanField(default=True)
    created_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'business'

    def __unicode__(self):
        return '%s' % self.name


class UserInformation(models.Model):
    business = models.ForeignKey(Business)
    created_time = models.DateTimeField(default=timezone.now)
    name = models.CharField('* Full Name', max_length=100)
    mitbbs_id = models.CharField('MITBBS ID', max_length=100, null=True, blank=True)
    endorse_mitbbs_id = models.CharField('背书人MITBBS ID', max_length=100, null=True, blank=True)
    email = models.EmailField('* Email', max_length=100)
    phone = models.CharField('* Phone', max_length=20)
    zip = models.CharField('Zip Code', max_length=10, null=True, blank=True)
    billpay_number = models.CharField('* Pill Pay Number', max_length=100)
    billpay_credit_card_type = models.CharField('* Pill Pay Credit Card Type', max_length=50)
    paid = models.FloatField(default=0)

    class Meta:
        db_table = 'user_information'

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.email)


class OrderDetail(models.Model):
    user = models.ForeignKey(UserInformation)
    order_number = models.CharField('Order Number', max_length=100)
    email = models.EmailField('Email', max_length=100)
    order_status = models.CharField(max_length=20, null=True, blank=True)
    shipping_status = models.CharField(max_length=20, null=True, blank=True)
    tracking_number = models.CharField(max_length=50, null=True, blank=True)
    ship_date = models.DateTimeField(null=True)
    deliver_date = models.DateTimeField(null=True)
    shipped = models.BooleanField(default=False)
    processing = models.BooleanField(default=False)
    on_hold = models.BooleanField(default=False)
    not_found = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

    class Meta:
        db_table = 'order_detail'

    def __unicode__(self):
        return '%s (%s) -- %s (%s)' % (self.order_number, self.email, self.user.name, self.user.email)
