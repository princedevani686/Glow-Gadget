import json
import os
from django.views.decorators.cache import never_cache
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .login_view import login_required
from core.settings import admin_role
from .models import CategoryVO, SubCategoryVO, ProductVO


# from base.models import CategoryVO


# @login_required(admin_role)
@never_cache
@login_required(admin_role)
def admin_add_product(request):
    category_vo_list = CategoryVO.objects.all()
    return render(request, 'admin/addProduct.html',
                  context={'category_vo_list': category_vo_list})


# @login_required(admin_role)
@never_cache
@login_required(admin_role)
def ajax_subcategory_product(request):
    category_id = request.GET.get('productCategoryId')

    category_vo = CategoryVO.objects.get(category_id=category_id)
    subcategory_vo_list = SubCategoryVO.objects.filter(
        subcategory_category_vo=category_vo)

    json_subcategory_vo_list = []
    for i in subcategory_vo_list:
        subcategory_vo_dict = model_to_dict(i)
        subcategory_vo_dict.pop("subcategory_image",None)
        json_subcategory_vo_list.append(subcategory_vo_dict)
    dump = json.dumps(json_subcategory_vo_list)
    return HttpResponse(dump, content_type='application/json')


# @login_required(admin_role)
@never_cache
@login_required(admin_role)
def admin_insert_product(request):
    product_vo = ProductVO()
    product_category_id = request.POST.get("productCategoryId")
    product_subcategory_id = request.POST.get("productSubcategoryId")

    product_vo.product_name = request.POST.get("product_name")
    product_vo.product_description = request.POST.get("product_description")
    product_vo.product_quantity = request.POST.get("product_quantity")
    product_vo.product_price = request.POST.get("product_price")
    product_vo.product_color = request.POST.get("product_color")
    product_vo.product_adjustable = request.POST.get("product_adjustable")
    product_vo.product_material = request.POST.get("product_material")
    product_vo.product_image = request.FILES["product_image"]

    category_vo = CategoryVO.objects.get(category_id=product_category_id)
    subcategory_vo = SubCategoryVO.objects.get(subcategory_id=product_subcategory_id)

    product_vo.product_category_id = category_vo
    product_vo.product_subcategory_id = subcategory_vo

    product_vo.save()

    return redirect('/admin_view_product')


# @login_required(admin_role)
@never_cache
@login_required(admin_role)
def admin_view_product(request):
    # product_vo_list = ProductVO.objects.select_related('product_category_id').select_related('product_subcategory_id').all()
    product_vo_list = ProductVO.objects.all()
    return render(request, "admin/viewProduct.html",
                  context={'product_vo_list': product_vo_list})


# @login_required(admin_role)
@never_cache
@login_required(admin_role)
def admin_delete_product(request):
    product_id = request.GET.get('product_id')
    product_vo = ProductVO.objects.get(product_id=product_id)
    os.remove(str(product_vo.product_image))
    product_vo.delete()
    return redirect('/admin_view_product')


# @login_required(admin_role)
@never_cache
@login_required(admin_role)
def admin_edit_product(request):
    product_id = request.GET.get('product_id')
    category_vo_list = CategoryVO.objects.all()
    subcategory_vo_list = SubCategoryVO.objects.all()
    product_vo_list = ProductVO.objects.get(product_id=product_id)
    os.remove(str(product_vo_list.product_image))

    return render(request, "admin/editProduct.html", context={
        'category_vo_list': category_vo_list,
        'subcategory_vo_list': subcategory_vo_list,
        'product_vo_list': product_vo_list})


# @login_required(admin_role)
@never_cache
@login_required(admin_role)
def admin_update_product(request):
    product_id = request.POST.get('product_id')
    product_category_id = request.POST.get('productCategoryId')
    product_subcategory_id = request.POST.get('productSubcategoryId')
    product_name = request.POST.get('productName')
    product_description = request.POST.get('productDescription')
    product_quantity = request.POST.get('productQuantity')
    product_price = request.POST.get('productPrice')
    product_image = request.FILES["product_image"]

    product_vo = ProductVO.objects.get(product_id=product_id)

    product_vo.product_name = product_name
    product_vo.product_description = product_description
    product_vo.product_price = product_price
    product_vo.product_quantity = product_quantity
    product_vo.product_image = product_image

    category_vo = CategoryVO.objects.get(category_id=product_category_id)
    subcategory_vo = SubCategoryVO.objects.get(
        subcategory_id=product_subcategory_id)

    product_vo.product_category_vo = category_vo
    product_vo.product_subcategory_vo = subcategory_vo
    product_vo.save()
    return redirect('/admin_view_product')

# @login_required(admin_role)
# def admin_edit_image_product(request):
#     product_id = request.GET.get("product_id")
#     product_vo_list = ProductVO.objects.filter(product_id=product_id)
#     return render(request, "admin/editProductImage.html", context= {'product_vo_list':product_vo_list})
#
# @login_required(admin_role)
# def admin_update_image_product(request):
#     product_id = request.POST.get('product_id')
#     product_image = request.FILES["product_image"]
#
#     product_vo = ProductVO.objects.get(product_id=product_id)
#     os.remove(str(product_vo.product_image))
#     product_vo.product_image = product_image
#     product_vo.save()
#     return redirect('/admin_view_product')
#
@never_cache
@login_required('user')
def user_load_product(request):
    subcategory_id = request.GET.get('subcategory_id')
    product_list = ProductVO.objects.filter(
        product_subcategory_id=subcategory_id)
    return render(request, "user/viewProduct.html",
                  {"product_list": product_list})

@never_cache
@login_required('user')
def user_product(request):
    return render(request, 'user/viewProduct.html')
@never_cache
@login_required('user')
def user_details_product(request):
    login_id = request.session.get('login_id')
    product_id = request.GET.get('product_id')
    product_list = ProductVO.objects.filter(product_id=product_id)
    return render(request,"user/viewDetailProduct.html",
                  {"product_list": product_list})
@never_cache
@login_required('user')
def user_products(request):
    product_list = ProductVO.objects.all()
    return render(request, "user/viewAllProduct.html",
                  {"product_list": product_list})
