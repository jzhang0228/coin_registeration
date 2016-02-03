from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import CollectOrderInformation, GetOrders, UpdateOrders, BusinessView, PayUser, DownloadOrders

urlpatterns = patterns('',
                       url(r'^$', CollectOrderInformation.as_view(), name='collect_order_information'),
                       url(r'^business/$', BusinessView.as_view(), name='business'),
                       url(r'^orders/(?P<business_id>\d+)/$', login_required(GetOrders.as_view()), name='get_orders'),
                       url(r'^update/(?P<business_id>\d+)/$', login_required(UpdateOrders.as_view()), name='update_orders'),
                       url(r'^pay_user/$', login_required(PayUser.as_view()), name='pay_user'),
                       url(r'^download/(?P<business_id>\d+)/$', login_required(DownloadOrders.as_view()), name='download'),
                       )
