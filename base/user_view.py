import bcrypt
from django.contrib import messages
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

from core.settings import admin_role
from .login_view import login_required
from .models import AreaVO, LoginVO, UserVO


# Create your views here.

def user_load_register(request):
    area_vo_list = AreaVO.objects.all()
    return render(request, 'user/register.html',
                  context={'area_vo_list': area_vo_list})


def user_insert_register(request):
    login_username = request.POST.get('loginUsername')
    login_password = request.POST.get('loginPassword')
    user_firstname = request.POST.get('userFirstname')
    user_lastname = request.POST.get('userLastname')
    user_gender = request.POST.get('userGender')
    user_area_id = request.POST.get('userArea')
    user_address = request.POST.get('userAddress')

    login_vo_list = LoginVO.objects.all()
    login_username_list = [model_to_dict(i)['login_username'] for i in
                           login_vo_list]

    if login_username in login_username_list:
        error_message = "The username is already exists !"
        messages.info(request, error_message)
        return redirect('/user_load_register')

    salt = bcrypt.gensalt(rounds=12)
    hashed_login_password = bcrypt.hashpw(login_password.encode("utf-8"),
                                          salt)

    login_vo = LoginVO()
    login_vo.login_username = login_username
    login_vo.login_password = (
        hashed_login_password.decode("utf-8"))
    login_vo.login_role = "user"
    login_vo.login_status = True
    login_vo.save()

    area_vo = AreaVO.objects.get(area_id=user_area_id)

    user_vo = UserVO()
    user_vo.user_firstname = user_firstname
    user_vo.user_lastname = user_lastname
    user_vo.user_gender = user_gender
    user_vo.user_address = user_address
    user_vo.user_area_vo = area_vo
    user_vo.user_login_vo = login_vo
    user_vo.save()
    return redirect("/")


@login_required(admin_role)
def admin_view_user(request):
    user_vo_list = UserVO.objects.select_related(
        'user_login_vo').select_related('user_area_vo').all()
    return render(request, 'admin/viewUser.html',
                  context={'user_vo_list': user_vo_list})
