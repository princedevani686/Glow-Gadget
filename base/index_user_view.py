from django.shortcuts import render
from .models import  OrderVO,CategoryVO
from django.views.decorators.cache import never_cache
from datetime import date
from .login_view import login_required


@never_cache
@login_required('user')
def user_load_home(request):
    category_list = CategoryVO.objects.all()
    return render(request, "user/index.html",
                  context={'category_list': category_list})
@never_cache
@login_required('user')
def user_about(request):
    return render(request, 'user/about.html')


@never_cache
@login_required('user')
def user_order(request):
    return render(request, 'user/billingDetail.html')


@never_cache
@login_required('user')
def user_thankyou(request):
    return render(request, 'user/thankyou.html')

@never_cache
@login_required('user')
def user_price(request):
    return render(request, "user/pricing.html")

@never_cache
def user_invoice(request):
    order_id = request.GET.get('order_id')
    print("order_id", order_id)
    order_list = OrderVO.objects.filter(order_id=order_id)
    print("order_list", order_list)

    today = date.today()
    print("today", today)
    return render(request, 'user/viewInvoice.html',
                  {'order_list': order_list, 'today': today})
