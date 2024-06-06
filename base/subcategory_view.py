import os

from django.shortcuts import render, redirect

from core.settings import admin_role
from .login_view import login_required
from .models import CategoryVO, SubCategoryVO
from django.views.decorators.cache import never_cache


@login_required(admin_role)
def admin_load_subcategory(request):
    category_vo_list = CategoryVO.objects.all()
    return render(request, 'admin/addSubcategory.html',
                  context={'category_vo_list':
                               category_vo_list})


@login_required(admin_role)
def admin_insert_subcategory(request):
    subcategory_image = request.FILES["subcategory_image"]
    subcategory_name = request.POST.get("subcategory_name")
    subcategory_description = request.POST.get(
        "subcategory_description")
    subcategory_category_id = request.POST.get("SubCategoryCategoryId")

    subcategory_vo = SubCategoryVO()
    category_vo = CategoryVO.objects.get(category_id=subcategory_category_id)
    subcategory_vo.subcategory_image = subcategory_image
    subcategory_vo.subcategory_name = subcategory_name
    subcategory_vo.subcategory_description = subcategory_description
    subcategory_vo.subcategory_category_vo = category_vo
    subcategory_vo.save()
    return redirect('/admin_view_subcategory')


@login_required(admin_role)
def admin_view_subcategory(request):
    # subcategory_vo_list = SubCategoryVO.objects.select_related('subcategory_category_vo').all()
    subcategory_vo_list = SubCategoryVO.objects.all()
    return render(request, 'admin/viewSubcategory.html',
                  context={'subcategory_vo_list': subcategory_vo_list})


@login_required(admin_role)
def admin_delete_subcategory(request):
    subcategory_id = request.GET.get('subcategory_id')
    subcategory_vo = SubCategoryVO.objects.get(subcategory_id=subcategory_id)
    os.remove(str(subcategory_vo.subcategory_image))

    subcategory_vo.delete()

    return redirect('/admin_view_subcategory')


@login_required(admin_role)
def admin_edit_subcategory(request):
    subcategory_id = request.GET.get('subcategory_id')

    subcategory_vo_list = SubCategoryVO.objects.get(
        subcategory_id=subcategory_id)
    category_vo_list = CategoryVO.objects.all()
    os.remove(str(subcategory_vo_list.subcategory_image))

    return render(request, "admin/editSubcategory.html",
                  context={'subcategory_vo_list': subcategory_vo_list,
                           'category_vo_list': category_vo_list})


@login_required(admin_role)
def admin_update_subcategory(request):
    subcategory_id = request.POST.get('subcategory_id')
    subcategory_image = request.FILES["subcategory_image"]
    subcategory_name = request.POST.get('subcategory_name')
    subcategory_description = request.POST.get('subcategory_description')
    subcategory_category_id = request.POST.get('SubCategoryCategoryId')

    subcategory_vo = SubCategoryVO()

    category_vo = CategoryVO.objects.get(category_id=subcategory_category_id)

    subcategory_vo.subcategory_id = subcategory_id
    subcategory_vo.subcategory_image = subcategory_image
    subcategory_vo.subcategory_name = subcategory_name
    subcategory_vo.subcategory_description = subcategory_description
    subcategory_vo.subcategory_category_vo = category_vo
    subcategory_vo.save()

    return redirect('/admin_view_subcategory')


@login_required('user')
def user_load_subcategory(request):
    category_id = request.GET.get("category_id")
    subcategory_list = SubCategoryVO.objects.filter(subcategory_category_vo=category_id)
    category_list = CategoryVO.objects.filter(category_id=category_id)
    return render(request, "user/viewSubCategory.html",
                  {"subcategory_list": subcategory_list, "category_list": category_list})

@never_cache
@login_required('user')
def user_subcategory(request):
    return render(request, 'user/viewSubCategory.html')