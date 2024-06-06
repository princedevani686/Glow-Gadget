import os

from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from base.models import CategoryVO
from core.settings import admin_role
from .login_view import login_required

@never_cache
@login_required(admin_role)
def admin_add_category(request):
    return render(request, 'admin/addCategory.html')

@never_cache
@login_required(admin_role)
def admin_insert_category(request):
    category_image = request.FILES['category_image']
    category_name = request.POST.get('category_name')
    category_description = request.POST.get('category_description')
    category_vo = CategoryVO()

    category_vo.category_image = category_image
    category_vo.category_name = category_name
    category_vo.category_description = category_description
    category_vo.save()
    return redirect('/admin_view_category')

@never_cache
@login_required(admin_role)
def admin_view_category(request):
    category_vo_list = CategoryVO.objects.all()
    return render(request, 'admin/viewCategory.html',
                  context={'category_vo_list': category_vo_list})

@never_cache
@login_required(admin_role)
def admin_delete_category(request):
    category_id = request.GET.get('category_id')
    category_vo = CategoryVO.objects.get(category_id=category_id)
    os.remove(str(category_vo.category_image))
    category_vo.delete()
    return redirect('/admin_view_category')

@never_cache
@login_required(admin_role)
def admin_edit_category(request):
    category_id = request.GET.get('category_id')
    category_vo_list = CategoryVO.objects.get(category_id=category_id)
    os.remove(str(category_vo_list.category_image))

    return render(request, 'admin/editCategory.html',
                  {'category_vo_list': category_vo_list})

@never_cache
@login_required(admin_role)
def admin_update_category(request):
    category_id = request.POST.get('category_id')
    category_image = request.FILES['category_image']
    category_name = request.POST.get('category_name')
    category_description = request.POST.get('category_description')

    category_vo = CategoryVO.objects.get(category_id=category_id)
    category_vo.category_image = category_image
    category_vo.category_name = category_name
    category_vo.category_description = category_description
    category_vo.save()
    return redirect('/admin_view_category')

@never_cache
@login_required('user')
def user_load_category(request):
    category_list = CategoryVO.objects.all()
    return render(request, "user/viewCategory.html",
                  {"category_list": category_list})

@never_cache
@login_required('user')
def user_category(request):
    return render(request, 'user/viewCategory.html')
