from django.forms import ModelForm
from .models import UserInformation, OrderDetail


class UserInformationForm(ModelForm):
    class Meta:
        model = UserInformation
        fields = ['name', 'mitbbs_id', 'endorse_mitbbs_id', 'email', 'phone', 'zip',
                  'billpay_number', 'billpay_credit_card_type']


class OrderDetailForm(ModelForm):
    class Meta:
        model = OrderDetail
        fields = ['order_number', 'email']
