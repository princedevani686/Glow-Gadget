from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from .login_view import login_required
from .models import AreaVO

@never_cache
@login_required('admin')
def admin_add_area(request):
    return render(request, 'admin/addArea.html')

@never_cache
@login_required('admin')
def admin_insert_area(request):
    area_name = request.POST.get('area_name')
    area_code = request.POST.get('area_code')
    area_vo = AreaVO()

    area_vo.area_name = area_name
    area_vo.area_code = area_code
    area_vo.save()
    return redirect('/admin_view_area')

@never_cache
@login_required('admin')
def admin_view_area(request):
    area_vo_list = AreaVO.objects.all()
    return render(request, 'admin/viewArea.html',
                  context={'area_vo_list': area_vo_list})

@never_cache
@login_required('admin')
def admin_delete_area(request):
    area_id = request.GET.get('area_id')
    area_vo = AreaVO.objects.get(area_id=area_id)
    area_vo.delete()
    return redirect('/admin_view_area')

@never_cache
@login_required('admin')
def admin_edit_area(request):
    area_id = request.GET.get('area_id')
    area_vo_list = AreaVO.objects.filter(area_id=area_id).all()
    return render(request, 'admin/editArea.html',
                  context={'area_vo_list': area_vo_list})

@never_cache
@login_required('admin')
def admin_update_area(request):
    area_id = request.POST.get('area_id')
    area_name = request.POST.get('area_name')
    area_code = request.POST.get('area_code')

    area_vo = AreaVO.objects.get(area_id=area_id)
    area_vo.area_name = area_name
    area_vo.area_code = area_code
    area_vo.save()
    return redirect('/admin_view_area')
