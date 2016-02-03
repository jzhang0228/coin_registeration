# -*- coding: utf-8 -*-
import csv
from datetime import datetime
from django.core.urlresolvers import reverse
from django.forms import formset_factory
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from order.forms import UserInformationForm, OrderDetailForm
from order.models import UserInformation, OrderDetail, Business
from order.parse_order import CheckOrders


class BusinessView(View):
    def get(self, request):
        businesses = Business.objects.all()
        context = {
            'businesses': businesses,
        }
        return render(request, 'order/all_business.html', context)



class CollectOrderInformation(View):
    OrderFormSet = formset_factory(OrderDetailForm)
    def get(self, request):
        user_form = UserInformationForm()
        order_formset = self.OrderFormSet()
        business = Business.objects.filter(active=True).order_by('-created_time')[0]
        context = {
            'user_form': user_form,
            'order_formset': order_formset,
            'business': business,
        }
        return render(request, 'order/user_and_order.html', context)

    def post(self, request):
        user_form = UserInformationForm(request.POST)
        order_formset = self.OrderFormSet(request.POST)
        if user_form.is_valid() and order_formset.is_valid():
            business = Business.objects.filter(active=True).order_by('-created_time')[0]
            user_information = user_form.save(commit=False)
            user_information.business = business
            user_information.save()
            for form in order_formset:
                order = form.save(commit=False)
                if not order.order_number and not order.email:
                    continue
                order.user = user_information
                order.save()
            return HttpResponse('Thank you! You have successfully submitted your order!')
        else:
            context = {
                'user_form': user_form,
                'order_formset': order_formset,
            }
            return render(request, 'order/user_and_order.html', context)

class GetOrders(View):
    def get(self, request, business_id):
        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            raise Http404

        users = UserInformation.objects.prefetch_related('orderdetail_set').filter(business_id=business_id)
        for user in users:
            orders = user.orderdetail_set.all()
            user.total_orders = len(orders)
            user.due = user.total_orders * business.profit
            user.unpaid = user.due - user.paid
        context = {
            'users': users,
            'business_id': business_id,
            'business': business,
        }
        return render(request, 'order/all_orders.html', context)


class UpdateOrders(View):
    def get_tracking_numbers(self, orders):
        MAX_COUNT = 2
        count = 0
        tracking_numbers = []
        for order in orders:
            if count < MAX_COUNT:
                tracking_numbers.append(order.tracking_number)
                count += 1
            else:
                yield tracking_numbers
                count = 1
                tracking_numbers = [order.tracking_number]
        yield tracking_numbers

    def get(self, request, business_id):
        orders = OrderDetail.objects.filter(user__business_id=business_id).exclude(shipping_status='Delivered')
        order_checker = CheckOrders()
        for order in orders:
            if order.order_status == 'SHIPPED':
                continue
            status, tracking, ship_date = order_checker.check_one_order(order.order_number, order.email)
            order.order_status = status
            order.tracking_number = tracking
            order.ship_date = datetime.strptime(ship_date, '%m/%d/%y')
            order.save()
        tracking_dictionary = {}
        for tracking_numbers in self.get_tracking_numbers(orders):
            tracking_dictionary.update(order_checker.check_shipping(tracking_numbers))
        for order in orders:
            status = tracking_dictionary[order.tracking_number]['status']
            deliver_date = tracking_dictionary[order.tracking_number]['deliver_date']
            if order.shipping_status != status:
                order.shipping_status = status
                if deliver_date:
                    order.deliver_date = datetime.strptime(deliver_date, '%m/%d/%Y')
                order.save()
        return redirect(reverse('get_orders', kwargs={'business_id': business_id}))


class PayUser(View):
    def get(self, request):
        user_id = request.GET['user_id']
        amount = request.GET['amount']
        try:
            user_information = UserInformation.objects.select_related('business').get(id=user_id)
        except UserInformation.DoesNotExist:
            raise Http404
        user_information.paid += float(amount)
        user_information.save()

        due = user_information.orderdetail_set.count() * user_information.business.profit
        context = {
            'success': True,
            'due_amount': due,
            'paid_amount': user_information.paid,
            'unpaid_amount': due - user_information.paid,
        }
        return JsonResponse(context)


class DownloadOrders(View):
    def get_number_and_emails(self, orders, delimiter):
        return delimiter.join([order.tracking_number + ' ' + order.email for order in orders])

    def get(self, request, business_id):
        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            raise Http404

        users = UserInformation.objects.prefetch_related('orderdetail_set').filter(business_id=business_id)

        response = HttpResponse(content_type='text/csv')
        file_name = '%s-%s.csv' % (business.name, datetime.now().strftime('%m/%d/%Y'))
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name

        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'Name', 'mitbbs id', '背书人mitbbs id', 'email', 'Phone', 'zip code',
                        '总order数', 'sent', 'available', 'tracking#', 'order number和配对email',
                        'billpay卡号', 'billpay 信用卡种类', 'due', 'paid', 'unpaid', 'Order Status', 'ship Date',
                        'Tracking', 'Shipping Status', 'Deliver Date', 'shipped', 'processing', 'on hold',
                        'not found', 'cancelled'])
        for user in users:
            orders = user.orderdetail_set.all()
            due = len(orders) * business.profit
            row = [user.created_time, user.name, user.mitbbs_id, user.endorse_mitbbs_id, user.email,
                   user.phone, user.zip, len(orders), '', '', '', self.get_number_and_emails(orders, '\n'),
                   user.billpay_number, user.billpay_credit_card_type, due, user.paid, due - user.paid,
                   '\n'.join([order.order_status for order in orders]),
                   '\n'.join([order.ship_date.strftime('%m/%d/%Y') for order in orders]),
                   '\n'.join([order.tracking_number for order in orders]),
                   '\n'.join([order.shipping_status for order in orders]),
                   '\n'.join([order.deliver_date.strftime('%m/%d/%Y') for order in orders]),
                   '\n'.join([str(order.shipped) for order in orders]),
                   '\n'.join([str(order.processing) for order in orders]),
                   '\n'.join([str(order.on_hold) for order in orders]),
                   '\n'.join([str(order.not_found) for order in orders]),
                   '\n'.join([str(order.cancelled) for order in orders])
            ]
            writer.writerow(row)

        return response


