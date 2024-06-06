from datetime import date, timedelta

from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from .login_view import login_required
from .models import (CartVO, UserVO,OrderVO, ProductVO)
import random

@never_cache
@login_required('user')
def user_insert_cart(request):
    cart_vo = CartVO()
    login_id = request.session.get('login_id')
    product_id = request.GET.get('product_id')
    product_list = ProductVO.objects.filter(product_id=product_id)

    abc = ProductVO.objects.get(product_id=product_id)
    print('abc?>?>?>?>?>?>',abc)
    price = abc.product_price

    cart_quantity = request.GET.get('cart_quantity')
    cart_subtotal = int(price) * int(cart_quantity)
    print('cart_quantity>>>>>>>>>>>>>>>><<<<<<<<<',cart_quantity)

    # cart_vo.cart_user_vo = UserVO.objects.get(user_login_vo=login_id)
    cart_user_vo = UserVO.objects.get(user_login_vo=login_id)
    cart_vo.cart_user_vo = cart_user_vo
    print("cart_user_vo>>>>>>>>>>>>",cart_user_vo)

    cart_vo.cart_product_vo = ProductVO.objects.get(product_id=product_id)
    cart_vo.cart_quantity = cart_quantity
    cart_vo.cart_subtotal = cart_subtotal

    cart_vo.save()
    return redirect('/user_cart')
@never_cache
@login_required('user')
def user_cart(request):
    login_id = request.session.get('login_id')
    user_list = UserVO.objects.get(user_login_vo=login_id)
    cart_list = CartVO.objects.filter(cart_user_vo=user_list.user_id)
    # cart_list = CartVO.objects.all()
    return render(request, 'user/viewCart.html',
                  context={'cart_list': cart_list})
@never_cache
@login_required('user')
def user_delete_cart(request):
    cart_id = request.GET.get('cart_id')
    cart_vo = CartVO.objects.get(cart_id=cart_id)
    cart_vo.cart_id = cart_id
    cart_vo.delete()

    return redirect('/user_cart')
@never_cache
@login_required('user')
def user_edit_cart(request):
    cart_id = request.GET.get('Id')
    cart_id, product_id = cart_id.split('-')
    print(">>>>>>>>>>>>>>>", cart_id, product_id)
    cart_list = CartVO.objects.get(cart_id=cart_id)
    product_list = ProductVO.objects.filter(product_id=product_id)

    return render(request,"user/editCart.html",
                  context={'cart_list': cart_list, 'product_list': product_list})
@never_cache
@login_required('user')
def user_update_cart(request):
    cart_id = request.GET.get('cart_id')
    print("cart_id", cart_id)
    login_id = request.session.get('login_id')

    product_id = request.GET.get('product_id')
    print("product_id", product_id)
    product_list = ProductVO.objects.filter(product_id=product_id)

    abc = ProductVO.objects.get(product_id=product_id)
    price = abc.product_price

    cart_quantity = request.GET.get('cart_quantity')
    cart_subtotal = int(price) * int(cart_quantity)

    cart_vo = CartVO()
    cart_vo = CartVO.objects.get(cart_id=cart_id)
    cart_vo.cart_user_vo = UserVO.objects.get(user_login_vo=login_id)
    cart_vo.cart_product_vo = ProductVO.objects.get(product_id=product_id)
    cart_vo.cart_quantity = cart_quantity
    cart_vo.cart_subtotal = cart_subtotal

    cart_vo.save()
    return redirect('/user_cart')
@never_cache
@login_required('user')
def user_order(request):
    login_id = request.session.get('login_id')
    user_list = UserVO.objects.get(user_login_vo=login_id)
    print(user_list)
    cart_list = CartVO.objects.filter(cart_user_vo=user_list.user_id)
    print("ssssssss",cart_list)
    cart_detail = []
    for cart in cart_list:
        product_name = cart.cart_product_vo.product_name
        cart_detail.append({
            'product_name' : product_name,
            'cart_quantity' : cart.cart_quantity,
            'cart_subtotal' : cart.cart_subtotal
        })
    print("aaaaaaaaaaaaa",cart_detail)

    total_price = 0
    for item in cart_detail:
        total_price = total_price + item['cart_subtotal']
    return render(request, 'user/billingDetail.html' , {'user_list' :user_list,
                                                        'cart_detail' : cart_detail, 'total_price' : total_price})
@never_cache
@login_required('user')
def user_insert_order(request):
    payment = request.GET.get('payment')
    login_id = request.session.get('login_id')
    user_list = UserVO.objects.get(user_login_vo=login_id)
    cart_list = CartVO.objects.filter(cart_user_vo=user_list.user_id)
    print(cart_list)

    for cart_item in cart_list:
        product_list = ProductVO.objects.get(product_id=cart_item.cart_product_vo.product_id)
        print(product_list)
        order_vo = OrderVO()
        order_vo.order_product_vo = product_list
        order_vo.order_user_vo = user_list
        order_vo.order_quantity = cart_item.cart_quantity
        order_vo.order_total = cart_item.cart_subtotal
        order_vo.order_date = date.today()
        order_vo.order_delivery_date = date.today()+timedelta(days=4)
        order_vo.order_status = payment
        order_vo.order_invoice = random.randint(10000000, 999999999)
        print(order_vo)
        order_vo.save()
    cart_list.delete()
    return render(request, 'user/thankyou.html')
    # return redirect('/user_view_order')

@never_cache
@login_required('user')
def user_view_order(request):
    login_id = request.session.get('login_id')
    print("aa", login_id)
    user_list = UserVO.objects.get(user_login_vo=login_id)
    order_list = OrderVO.objects.filter(order_user_vo=user_list)
    print("order list", order_list)

    return render(request, 'user/viewOrder.html',
                  {'user_list': user_list, 'order_list': order_list, })
@never_cache
@login_required('user')
def user_delete_order(request):
    order_id = request.GET.get('order_id')
    order_vo = OrderVO.objects.get(order_id=order_id)
    order_vo.order_id = order_id
    order_vo.delete()

    return redirect('/user_view_order')
@never_cache
@login_required('admin')
def admin_view_order(request):
    order_list = OrderVO.objects.all()
    print(order_list)

    return render(request, 'admin/viewOrder.html',
                  context={'order_list': order_list})

