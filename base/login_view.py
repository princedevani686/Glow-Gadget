import random
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from .models import UserVO,ProductVO,OrderVO,CategoryVO
import bcrypt
import httpagentparser
import jwt
from django.contrib import messages
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

from core.settings import SECRET_KEY
from core.settings import config
from .models import LoginVO, DeviceInfoVO ,ComplainVO ,SubCategoryVO


def get_client_identity(request):
    print("get_client_identity")
    remote_addr = request.META.get('REMOTE_ADDR')
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', remote_addr)

    agent = request.environ.get('HTTP_USER_AGENT')
    browser = httpagentparser.detect(agent)
    if not browser:
        browser = agent.split('/')[0]
    else:
        browser = browser['browser']['name']

    return "{}:{}".format(ip_addr, browser)


def insert_client_identity(request, login_id):
    print("insert_client_identity")
    # try:
    print(">>>>>>>>>IN")
    device_info_vo = DeviceInfoVO()

    device_list = DeviceInfoVO.objects.filter(device_login_vo_id=login_id)

    for device in device_list:
        if bcrypt.checkpw(get_client_identity(request).encode(
                config.get("ALGORITHMS", "ENCODING")),
                device.device_identity.encode(
                    config.get("ALGORITHMS", "ENCODING"))):
            device_info_vo = device
            print("????????device_info", device_info_vo)
            break

    hashed_client_identity = bcrypt.hashpw(
        get_client_identity(request).encode(
            config.get("ALGORITHMS", "ENCODING")),
        bcrypt.gensalt(rounds=12))
    device_info_vo.device_identity = hashed_client_identity.decode(
        config.get("ALGORITHMS", "ENCODING"))
    device_info_vo.device_login_vo_id = login_id

    device_info_vo.save()


# except Exception as ex:
#     print("insert_client_identity_exception>>>>>>>>>>>>", ex)


def refresh_token(request, fn):
    # try:
    refreshtoken = request.COOKIES.get(
        config.get("TOKENS", "REFRESHTOKEN"))

    if refreshtoken is not None:
        print(">>>>>>>>>refreshtoken", refreshtoken)
        data = jwt.decode(refreshtoken, SECRET_KEY,
                          config.get("ALGORITHMS", "HASH_ALGORITHM"))

        login_vo_list = LoginVO.objects.filter(
            login_username=data['public_id'])
        print(">>>>>>", login_vo_list)

        device_list = DeviceInfoVO.objects.filter(
            device_login_vo_id=login_vo_list[0].login_id).all()

        for device in device_list:
            if bcrypt.checkpw(get_client_identity(request).encode(
                    config.get("ALGORITHMS", "ENCODING")),
                    device.device_identity.encode(
                        config.get("ALGORITHMS", "ENCODING"))):
                print('Device Matched')

                response = fn(request)
                response.set_cookie(config.get("TOKENS", "ACCESSTOKEN"),
                                    value=jwt.encode({
                                        'public_id': login_vo_list[
                                            0].login_username,
                                        'role': login_vo_list[
                                            0].login_role,
                                        'exp': datetime.utcnow() + timedelta(
                                            minutes=config.getint("TIME",
                                                                  "ACCESS_TOKEN_EXP"))
                                    }, SECRET_KEY, config.get("ALGORITHMS",
                                                              "HASH_ALGORITHM")),
                                    max_age=config.getint("TIME",
                                                          "ACCESS_TOKEN_MAX_AGE"))
                refresh = jwt.encode({
                    'public_id': login_vo_list[0].login_username,
                    'exp': datetime.utcnow() + timedelta(
                        hours=config.getint("TIME", "REFRESH_TOKEN_EXP"))
                }, SECRET_KEY, config.get("ALGORITHMS", "HASH_ALGORITHM"))

                print('Token Refreshed Successfully')
                response.set_cookie(config.get("TOKENS", "REFRESHTOKEN"),
                                    value=refresh,
                                    max_age=config.getint("TIME",
                                                          "REFRESH_TOKEN_MAX_AGE"))
                return response
        else:
            error_message = 'We Encounterd Malicious Activity Please Re-Login'
            messages.info(request, error_message)
            return admin_logout_session(request,
                                        login_vo_list[0].login_username)
    else:
        error_message = 'Unauthorized Access'
        messages.info(request, error_message)
        return admin_logout_session(request)


# except Exception as ex:
#     print('Exception in Refreshing Token', ex)
#     error_message = 'Session expired'
#     messages.info(request, error_message)
#     return admin_logout_session(request)


def login_required(role):
    def inner(fn):
        @wraps(fn)
        def decorator(request):
            try:
                accesstoken = request.COOKIES.get(
                    config.get("TOKENS", "ACCESSTOKEN"))

                if accesstoken is None:
                    print(">>>>>>>accesstoken")
                    return refresh_token(request, fn)
                else:
                    data = jwt.decode(accesstoken, SECRET_KEY,
                                      config.get("ALGORITHMS",
                                                 "HASH_ALGORITHM"))
                    print("data")
                    login_vo_list = LoginVO.objects.filter(
                        login_username=data['public_id'])
                    if login_vo_list is not None:
                        login_list = [model_to_dict(i) for i in login_vo_list]

                        if login_list[0]['login_status'] == 1 and data[
                            'role'] == role:
                            return fn(request)
                        else:
                            return redirect('/')
                    else:
                        error_message = 'Unauthorized Access'
                        messages.info(request, error_message)
                        return redirect('/')
            except Exception as ex:
                print("login_required route Exception>>>>", ex)
                return refresh_token(request, fn)

        return decorator

    return inner


def admin_load_login(request):
    # try:
    return render(request, 'admin/login.html')


# except Exception as ex:
#     print("user_load_login route exception occured>>>>>>>>>>", ex)
#     return render(request, 'user/viewError.html', context={'message': ex})


def admin_validate_login(request):
    # try:
    login_username = request.POST.get('loginUsername')
    login_password = request.POST.get('loginPassword').encode(
        config.get("ALGORITHMS", "ENCODING"))
    print(">>>>>>>>>>>>validate_login", login_password)
    login_vo_list = LoginVO.objects.filter(login_username=login_username)
    if len(login_vo_list) == 0:
        error_message = 'username is incorrect !'
        messages.info(request, error_message)
        return redirect('/')
    else:
        login_dict = model_to_dict(login_vo_list[0])
        if not login_dict['login_status']:
            error_message = 'You have been temporarily blocked by admin !'
            messages.info(request, error_message)
            return redirect('/')
        else:
            login_id = login_dict['login_id']
            login_username = login_dict['login_username']
            login_role = login_dict['login_role']

            hashed_login_password = login_dict['login_password'] \
                .encode(config.get("ALGORITHMS", "ENCODING"))
            print("???????hased pwd", hashed_login_password)
            if bcrypt.checkpw(login_password, hashed_login_password):
                insert_client_identity(request, login_id)

                if login_role == 'admin':
                    response = redirect(admin_load_dashboard)
                    response.set_cookie(
                        config.get("TOKENS", "ACCESSTOKEN"),
                        value=jwt.encode({
                            'public_id': login_username,
                            'role': login_role,
                            'exp': datetime.utcnow() + timedelta(
                                minutes=config.getint("TIME",
                                                      "ACCESS_TOKEN_EXP"))
                        }, SECRET_KEY,
                            config.get("ALGORITHMS", "HASH_ALGORITHM")),
                        max_age=config.getint("TIME",
                                              "ACCESS_TOKEN_MAX_AGE"))
                    print("123")
                    refresh = jwt.encode({
                        'public_id': login_username,
                        'exp': datetime.utcnow() + timedelta(
                            hours=config.getint("TIME",
                                                "REFRESH_TOKEN_EXP"))
                    }, SECRET_KEY,
                        config.get("ALGORITHMS", "HASH_ALGORITHM"))

                    response.set_cookie(
                        config.get("TOKENS", "REFRESHTOKEN"),
                        value=refresh,
                        max_age=config.getint("TIME",
                                              "REFRESH_TOKEN_MAX_AGE"))
                    return response

                elif login_role == 'user':
                    response = redirect(f'/user_load_dashboard?loginId={login_id}')
                    response.set_cookie(
                        config.get("TOKENS", "ACCESSTOKEN"),
                        value=jwt.encode({
                            'public_id': login_username,
                            'role': login_role,
                            'exp': datetime.utcnow() + timedelta(
                                minutes=config.getint("TIME",
                                                      "ACCESS_TOKEN_EXP"))
                        }, SECRET_KEY,
                            config.get("ALGORITHMS", "HASH_ALGORITHM")),
                        max_age=config.getint("TIME",
                                              "ACCESS_TOKEN_MAX_AGE"))

                    refresh = jwt.encode({
                        'public_id': login_username,
                        'exp': datetime.utcnow() + timedelta(
                            hours=config.getint("TIME",
                                                "REFRESH_TOKEN_EXP"))
                    }, SECRET_KEY,
                        config.get("ALGORITHMS", "HASH_ALGORITHM"))

                    response.set_cookie(
                        config.get("TOKENS", "REFRESHTOKEN"),
                        value=refresh,
                        max_age=config.getint("TIME",
                                              "REFRESH_TOKEN_MAX_AGE"))
                    return response
                else:
                    return redirect(admin_logout_session)
            else:
                error_message = 'password is incorrect !'
                messages.info(request, error_message)
                return redirect('/')


# except Exception as ex:
#     print("admin_validate_login route exception occured>>>>>>>>>>", ex)
#     return render(request, 'user/viewError.html', context={'message': ex})

@never_cache
@login_required('admin')
def admin_load_dashboard(request):
    user_list = UserVO.objects.all()
    category_list = CategoryVO.objects.all()
    subcategory_list = SubCategoryVO.objects.all()
    product_list = ProductVO.objects.all()
    order_list = OrderVO.objects.all()
    Complain_list = ComplainVO.objects.all()

    user = len(user_list)
    category = len(category_list)
    subcategory = len(subcategory_list)
    product = len(product_list)
    order = len(order_list)
    complain = len(Complain_list)
    return render(request, "admin/index.html",
                  context={'user': user, 'product': product, 'order': order,
                           'complain': complain, 'category': category,
                           'subcategory': subcategory})


# except Exception as ex:
#     print("in admin_load_dashboard function exception occured>>>>>", ex)
#     return render(request, 'admin/viewError.html', context={'message': ex})

@never_cache
@login_required('user')
def user_load_dashboard(request):
    login_id = request.GET.get('loginId')
    request.session['login_id'] = login_id
    category_list = CategoryVO.objects.all()
    return render(request, "user/index.html" ,context={'category_list':category_list})


def admin_logout_session(request, *user_name):
    # try:
    if len(user_name) != 0 and user_name[0] is not None:
        login_vo = LoginVO()

        login_vo.login_username = user_name[0]

        login_vo_list = LoginVO.objects.filter(
            login_username=login_vo.login_username).all()

        login_id = login_vo_list[0].login_id

        device_list = DeviceInfoVO.objects. \
            filter(device_login_vo_id=login_id).all()
        for device_vo in device_list:
            device_vo.delete()

        response = redirect('/')
        response.set_cookie(config.get("TOKENS", "ACCESSTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        response.set_cookie(config.get("TOKENS", "REFRESHTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        return response

    elif request.COOKIES.get(
            config.get("TOKENS", "REFRESHTOKEN")) is not None:
        refreshtoken = request.COOKIES.get(
            config.get("TOKENS", "REFRESHTOKEN"))

        data = jwt.decode(refreshtoken, SECRET_KEY,
                          config.get("ALGORITHMS", "HASH_ALGORITHM"))

        login_vo = LoginVO()
        device_vo = DeviceInfoVO()

        login_vo.login_username = data['public_id']

        login_vo_list = LoginVO.objects.filter(login_username=login_vo.login_username).all()

        login_vo = login_vo_list[0]

        device_list = DeviceInfoVO.objects.filter(device_login_vo_id=login_vo.login_id).all()
        if len(device_list) != 0:
            for device in device_list:
                if bcrypt.checkpw(get_client_identity(request).encode(
                        config.get("ALGORITHMS", "ENCODING")),
                        device.device_identity.encode(
                            config.get("ALGORITHMS", "ENCODING"))):
                    device_vo = device
                    break
            device_vo = DeviceInfoVO.objects.get(device_id=device_vo.device_id)
            device_vo.delete()
        response = redirect('/')
        response.set_cookie(config.get("TOKENS", "ACCESSTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        response.set_cookie(config.get("TOKENS", "REFRESHTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        return response

    else:
        response = redirect('/')
        response.set_cookie(config.get("TOKENS", "ACCESSTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        response.set_cookie(config.get("TOKENS", "REFRESHTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        return response


# except Exception as ex:
#     print("admin_logout_session route exception occured>>>>>>>>>>", ex)
#     return render(request, 'user/viewError.html', context={'message': ex})

@never_cache
@login_required('user')
def user_logout(request, *user_name):
    # try:
    if len(user_name) != 0 and user_name[0] is not None:
        login_vo = LoginVO()

        login_vo.login_username = user_name[0]

        login_vo_list = LoginVO.objects.filter(
            login_username=login_vo.login_username).all()

        login_id = login_vo_list[0].login_id

        device_list = DeviceInfoVO.objects. \
            filter(device_login_vo_id=login_id).all()
        for device_vo in device_list:
            device_vo.delete()

        response = redirect('/')
        response.set_cookie(config.get("TOKENS", "ACCESSTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        response.set_cookie(config.get("TOKENS", "REFRESHTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        return response

    elif request.COOKIES.get(
            config.get("TOKENS", "REFRESHTOKEN")) is not None:
        refreshtoken = request.COOKIES.get(
            config.get("TOKENS", "REFRESHTOKEN"))

        data = jwt.decode(refreshtoken, SECRET_KEY,
                          config.get("ALGORITHMS", "HASH_ALGORITHM"))

        login_vo = LoginVO()
        device_vo = DeviceInfoVO()

        login_vo.login_username = data['public_id']

        login_vo_list = LoginVO.objects.filter(
            login_username=login_vo.login_username).all()

        login_vo = login_vo_list[0]

        device_list = DeviceInfoVO.objects.filter(
            device_login_vo_id=login_vo.login_id).all()
        if len(device_list) != 0:
            for device in device_list:
                if bcrypt.checkpw(get_client_identity(request).encode(
                        config.get("ALGORITHMS", "ENCODING")),
                        device.device_identity.encode(
                            config.get("ALGORITHMS", "ENCODING"))):
                    device_vo = device
                    break
            device_vo = DeviceInfoVO.objects.get(device_id
                                                 =device_vo.device_id)
            device_vo.delete()
        response = redirect('/')
        response.set_cookie(config.get("TOKENS", "ACCESSTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        response.set_cookie(config.get("TOKENS", "REFRESHTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        return response

    else:
        response = redirect('/')
        response.set_cookie(config.get("TOKENS", "ACCESSTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        response.set_cookie(config.get("TOKENS", "REFRESHTOKEN"),
                            max_age=config.getint("TIME",
                                                  "TIME_OUT_MAX_AGE"))
        return response
@login_required('admin')
def admin_block_user(request):
    # try:
    login_id = request.GET.get('loginId')
    login_vo = LoginVO.objects.get(login_id=login_id)
    login_vo.login_status = False
    login_vo.save()
    return redirect("/admin_view_user")


# except Exception as ex:
#     print("admin_block_user route exception occured>>>>>>>>>>", ex)
#     return render(request, 'admin/viewError.html', context={'message': ex})


@login_required('admin')
def admin_unblock_user(request):
    # try:
    login_id = request.GET.get('loginId')
    login_vo = LoginVO.objects.get(login_id=login_id)
    login_vo.login_status = True
    login_vo.save()
    return redirect('/admin_view_user')


# except Exception as ex:
#     print("admin_unblock_user route exception occured>>>>>>>>>>", ex)
#     return render(request, 'admin/viewError.html', context={'message': ex})

def user_load_forget_password(request):
    # try:
    return render(request, 'user/forgetPassword.html')


# except Exception as ex:
#     print("user_load_forget_password route exception occured>>>>>>>>>>",
#           ex)
#     return render(request, 'user/viewError.html', context={'message': ex})
def user_validate_login_username(request):
    # try:
    login_username = request.POST.get("loginUsername")
    login_vo_list = LoginVO.objects.filter(login_username=login_username)
    login_list = [model_to_dict(i) for i in login_vo_list]
    len_login_list = len(login_list)
    if len_login_list == 0:
        error_message = 'username is incorrect !'
        messages.info(request, error_message)
        return redirect('/user/load_forget_password')
    else:
        login_id = login_list[0]['login_id']
        request.session['session_login_id'] = login_id
        login_username = login_list[0]['login_username']
        sender = "noreplypython@yahoo.com"
        receiver = login_username
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = "PYTHON OTP"
        otp = random.randint(1000, 9999)
        request.session['session_otp_number'] = otp
        message = str(otp)
        msg.attach(MIMEText(message, 'plain'))
        server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
        server.starttls()
        server.login(sender, "dbzivjinwbndvvey")
        text = msg.as_string()
        server.sendmail(sender, receiver, text)
        server.quit()
        return render(request, 'user/otpValidation.html')


# except Exception as ex:
#     print("user_validate_login_username route exception occured>>>>>>>>>>",
#           ex)
#     return render(request, 'user/viewError.html', context={'message': ex})


def user_validate_otp_number(request):
    # try:
    otp_number = int(request.POST.get("otpNumber"))
    session_otp_number = request.session.get('session_otp_number')
    if otp_number == session_otp_number:
        return render(request, 'user/resetPassword.html')
    else:
        request.session.flush()

        error_message = 'otp is incorrect !'
        messages.info(request, error_message)
        return redirect('/user/load_forget_password')


# except Exception as ex:
#     print("user_validate_otp_number route exception occured>>>>>>>>>>", ex)
#     return render(request, 'user/viewError.html', context={'message': ex})


def user_insert_reset_password(request):
    # try:
    login_password = request.POST.get("loginPassword")
    salt = bcrypt.gensalt(rounds=12)
    hashed_login_password = bcrypt.hashpw(
        login_password.encode(config.get("ALGORITHMS", "ENCODING")),
        salt).decode(config.get("ALGORITHMS", "ENCODING"))
    login_id = request.session.get("session_login_id")
    login_vo = LoginVO.objects.get(login_id=login_id)
    login_vo.login_password = hashed_login_password
    login_vo.save()
    return redirect('/')
# except Exception as ex:
#     print("user_insert_reset_password route exception occured>>>>>>>>>>",
#           ex)
#     return render(request, 'user/viewError.html', context={'message': ex})

# import random
# import smtplib
# from datetime import datetime, timedelta
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from functools import wraps
#
# import bcrypt
# import httpagentparser
# import jwt
# from django.contrib import messages
# from django.forms import model_to_dict
# from django.shortcuts import redirect
# from django.shortcuts import render
#
# from core.settings import SECRET_KEY
# from core.settings import config
# from .models import LoginVO, DeviceInfoVO
#
#
# def get_client_identity(request):
#     remote_addr = request.META.get('REMOTE_ADDR')
#     ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', remote_addr)
#     print("ip_addr>>>>>>>>>>>>>>>>", ip_addr)
#
#     agent = request.environ.get('HTTP_USER_AGENT')
#     browser = httpagentparser.detect(agent)
#     if not browser:
#         browser = agent.split('/')[0]
#     else:
#         browser = browser['browser']['name']
#
#     return "{}:{}".format(ip_addr, browser)
#
#
# def insert_client_identity(request, login_id):
#     device_info_vo = DeviceInfoVO()
#
#     device_list = DeviceInfoVO.objects.filter(device_login_vo_id=login_id)
#
#     for device in device_list:
#         if bcrypt.checkpw(get_client_identity(request).encode(
#                 config.get("ALGORITHMS", "ENCODING")),
#                 device.device_identity.encode(
#                     config.get("ALGORITHMS", "ENCODING"))):
#             device_info_vo = device
#             break
#
#     hashed_client_identity = bcrypt.hashpw(
#         get_client_identity(request).encode(
#             config.get("ALGORITHMS", "ENCODING")),
#         bcrypt.gensalt(rounds=12))
#     device_info_vo.device_identity = hashed_client_identity.decode(
#         config.get("ALGORITHMS", "ENCODING"))
#     device_info_vo.device_login_vo_id = login_id
#
#     device_info_vo.save()
#
#
# def refresh_token(request, fn):
#     print("in")
#     refreshtoken = request.COOKIES.get(
#         config.get("TOKENS", "REFRESHTOKEN"))
#     print("refreshtoken>>>>>>>>", refreshtoken)
#     if refreshtoken is not None:
#         print("insert")
#         data = jwt.decode(refreshtoken, SECRET_KEY,
#                           config.get("ALGORITHMS", "HASH_ALGORITHM"))
#         print("data------------", data)
#         login_vo_list = LoginVO.objects.filter(
#             login_username=data['public_id'])
#         print("login_vo_list--------->", login_vo_list)
#         device_list = DeviceInfoVO.objects.filter(
#             device_login_vo_id=login_vo_list[0].login_id).all()
#
#         for device in device_list:
#             print('In Token Refresh')
#             if bcrypt.checkpw(get_client_identity(request).encode(
#                     config.get("ALGORITHMS", "ENCODING")),
#                     device.device_identity.encode(
#                         config.get("ALGORITHMS", "ENCODING"))):
#                 print('Device Matched')
#
#                 response = fn(request)
#                 response.set_cookie(config.get("TOKENS", "ACCESSTOKEN"),
#                                     value=jwt.encode({
#                                         'public_id': login_vo_list[
#                                             0].login_username,
#                                         'role': login_vo_list[
#                                             0].login_role,
#                                         'exp': datetime.utcnow() + timedelta(
#                                             minutes=config.getint("TIME",
#                                                                   "ACCESS_TOKEN_EXP"))
#                                     }, SECRET_KEY, config.get("ALGORITHMS",
#                                                               "HASH_ALGORITHM")),
#                                     max_age=config.getint("TIME",
#                                                           "ACCESS_TOKEN_MAX_AGE"))
#                 refresh = jwt.encode({
#                     'public_id': login_vo_list[0].login_username,
#                     'exp': datetime.utcnow() + timedelta(
#                         hours=config.getint("TIME", "REFRESH_TOKEN_EXP"))
#                 }, SECRET_KEY, config.get("ALGORITHMS", "HASH_ALGORITHM"))
#
#                 print('Token Refreshed Successfully')
#                 response.set_cookie(config.get("TOKENS", "REFRESHTOKEN"),
#                                     value=refresh,
#                                     max_age=config.getint("TIME",
#                                                           "REFRESH_TOKEN_MAX_AGE"))
#                 return response
#         else:
#             error_message = 'We Encounterd Malicious Activity Please Re-Login'
#             messages.info(request, error_message)
#             return admin_logout_session(request,
#                                         login_vo_list[0].login_username)
#     else:
#         error_message = 'Unauthorized Access'
#         messages.info(request, error_message)
#         return admin_logout_session(request)
#
#
# def login_required(role):
#     def inner(fn):
#         @wraps(fn)
#         def decorator(request):
#             # try:
#             accesstoken = request.COOKIES.get(
#                 config.get("TOKENS", "ACCESSTOKEN"))
#             print("Access Token------>>>>>", accesstoken)
#             if accesstoken is None:
#                 return refresh_token(request, fn)
#             else:
#                 print("new")
#                 data = jwt.decode(accesstoken, SECRET_KEY,
#                                   config.get("ALGORITHMS",
#                                              "HASH_ALGORITHM"))
#                 login_vo_list = LoginVO.objects.filter(
#                     login_username=data['public_id'])
#                 print(">>>>>>>>>>>>>>>>>>>>>>>>>>.---", data)
#                 if login_vo_list is not None:
#                     login_list = [model_to_dict(i) for i in login_vo_list]
#
#                     if login_list[0]['login_status'] == 1 and data[
#                         'role'] == role:
#                         return fn(request)
#                     else:
#                         return redirect('/')
#                 else:
#                     error_message = 'Unauthorized Access'
#                     messages.info(request, error_message)
#                     return redirect('/')
#
#         # except Exception as ex:
#         #     print("login_required route Exception>>>>", ex)
#         #     print("refresh_token-----=>>>>>",refresh_token)
#         #     return refresh_token(request, fn)
#
#         return decorator
#
#     return inner
#
#
# def admin_load_login(request):
#     return render(request, 'admin/login.html')
#
#
# def admin_validate_login(request):
#     login_username = request.POST.get('loginUsername')
#     login_password = request.POST.get('loginPassword').encode(
#         config.get("ALGORITHMS", "ENCODING"))
#
#     login_vo_list = LoginVO.objects.filter(login_username=login_username)
#     if len(login_vo_list) == 0:
#         error_message = 'username is incorrect !'
#         messages.info(request, error_message)
#         return redirect('/')
#     else:
#         login_dict = model_to_dict(login_vo_list[0])
#         if not login_dict['login_status']:
#             error_message = 'You have been temporarily blocked by admin !'
#             messages.info(request, error_message)
#             return redirect('/')
#         else:
#             login_id = login_dict['login_id']
#             login_username = login_dict['login_username']
#             login_role = login_dict['login_role']
#
#             hashed_login_password = login_dict['login_password'] \
#                 .encode(config.get("ALGORITHMS", "ENCODING"))
#             if bcrypt.checkpw(login_password, hashed_login_password):
#                 insert_client_identity(request, login_id)
#
#                 if login_role == 'admin':
#                     response = redirect(admin_load_dashboard)
#                     response.set_cookie(
#                         config.get("TOKENS", "ACCESSTOKEN"),
#                         value=jwt.encode({
#                             'public_id': login_username,
#                             'role': login_role,
#                             'exp': datetime.utcnow() + timedelta(
#                                 minutes=config.getint("TIME",
#                                                       "ACCESS_TOKEN_EXP"))
#                         }, SECRET_KEY,
#                             config.get("ALGORITHMS", "HASH_ALGORITHM")),
#                         max_age=config.getint("TIME",
#                                               "ACCESS_TOKEN_MAX_AGE"))
#
#                     refresh = jwt.encode({
#                         'public_id': login_username,
#                         'exp': datetime.utcnow() + timedelta(
#                             hours=config.getint("TIME",
#                                                 "REFRESH_TOKEN_EXP"))
#                     }, SECRET_KEY,
#                         config.get("ALGORITHMS", "HASH_ALGORITHM"))
#
#                     response.set_cookie(
#                         config.get("TOKENS", "REFRESHTOKEN"),
#                         value=refresh,
#                         max_age=config.getint("TIME",
#                                               "REFRESH_TOKEN_MAX_AGE"))
#                     return response
#
#                 elif login_role == 'user':
#                     print("User----->>>>>>>>>")
#                     response = redirect(f'/user_load_dashboard?loginId={login_id}')
#                     response.set_cookie(
#                         config.get("TOKENS", "ACCESSTOKEN"),
#                         value=jwt.encode({
#                             'public_id': login_username,
#                             'role': login_role,
#                             'exp': datetime.utcnow() + timedelta(
#                                 minutes=config.getint("TIME",
#                                                       "ACCESS_TOKEN_EXP"))
#                         }, SECRET_KEY,
#                             config.get("ALGORITHMS", "HASH_ALGORITHM")),
#                         max_age=config.getint("TIME",
#                                               "ACCESS_TOKEN_MAX_AGE"))
#
#                     refresh = jwt.encode({
#                         'public_id': login_username,
#                         'exp': datetime.utcnow() + timedelta(
#                             hours=config.getint("TIME",
#                                                 "REFRESH_TOKEN_EXP"))
#                     }, SECRET_KEY,
#                         config.get("ALGORITHMS", "HASH_ALGORITHM"))
#
#                     response.set_cookie(
#                         config.get("TOKENS", "REFRESHTOKEN"),
#                         value=refresh,
#                         max_age=config.getint("TIME",
#                                               "REFRESH_TOKEN_MAX_AGE"))
#                     return response
#                 else:
#                     return redirect(admin_logout_session)
#             else:
#                 error_message = 'password is incorrect !'
#                 messages.info(request, error_message)
#                 return redirect('/')
#
#
# @login_required('admin')
# def admin_load_dashboard(request):
#     return render(request, "admin/index.html")
#
#
# @login_required('user')
# def user_load_dashboard(request):
#     login_id = request.GET.get('loginId')
#     request.session['loginId'] = login_id
#     return render(request, "user/index.html")
#
#
# def admin_logout_session(request, *user_name):
#     if len(user_name) != 0 and user_name[0] is not None:
#         login_vo = LoginVO()
#
#         login_vo.login_username = user_name[0]
#
#         login_vo_list = LoginVO.objects.filter(
#             login_username=login_vo.login_username).all()
#
#         login_id = login_vo_list[0].login_id
#
#         device_list = DeviceInfoVO.objects. \
#             filter(device_login_vo_id=login_id).all()
#         for device_vo in device_list:
#             device_vo.delete()
#
#         response = redirect('/')
#         response.set_cookie(config.get("TOKENS", "ACCESSTOKEN"),
#                             max_age=config.getint("TIME",
#                                                   "TIME_OUT_MAX_AGE"))
#         response.set_cookie(config.get("TOKENS", "REFRESHTOKEN"),
#                             max_age=config.getint("TIME",
#                                                   "TIME_OUT_MAX_AGE"))
#         return response
#
#     elif request.COOKIES.get(
#             config.get("TOKENS", "REFRESHTOKEN")) is not None:
#         refreshtoken = request.COOKIES.get(
#             config.get("TOKENS", "REFRESHTOKEN"))
#
#         data = jwt.decode(refreshtoken, SECRET_KEY,
#                           config.get("ALGORITHMS", "HASH_ALGORITHM"))
#
#         login_vo = LoginVO()
#         device_vo = DeviceInfoVO()
#
#         login_vo.login_username = data['public_id']
#
#         login_vo_list = LoginVO.objects.filter(
#             login_username=login_vo.login_username).all()
#
#         login_vo = login_vo_list[0]
#
#         device_list = DeviceInfoVO.objects.filter(
#             device_login_vo_id=login_vo.login_id).all()
#         if len(device_list) != 0:
#             for device in device_list:
#                 if bcrypt.checkpw(get_client_identity(request).encode(
#                         config.get("ALGORITHMS", "ENCODING")),
#                         device.device_identity.encode(
#                             config.get("ALGORITHMS", "ENCODING"))):
#                     device_vo = device
#                     break
#             device_vo = DeviceInfoVO.objects.get(device_id
#                                                  =device_vo.device_id)
#             device_vo.delete()
#         response = redirect('/')
#         response.set_cookie(config.get("TOKENS", "ACCESSTOKEN"),
#                             max_age=config.getint("TIME",
#                                                   "TIME_OUT_MAX_AGE"))
#         response.set_cookie(config.get("TOKENS", "REFRESHTOKEN"),
#                             max_age=config.getint("TIME",
#                                                   "TIME_OUT_MAX_AGE"))
#         return response
#
#     else:
#         response = redirect('/')
#         response.set_cookie(config.get("TOKENS", "ACCESSTOKEN"),
#                             max_age=config.getint("TIME",
#                                                   "TIME_OUT_MAX_AGE"))
#         response.set_cookie(config.get("TOKENS", "REFRESHTOKEN"),
#                             max_age=config.getint("TIME",
#                                                   "TIME_OUT_MAX_AGE"))
#         return response
#
#
# @login_required('admin')
# def admin_block_user(request):
#     login_id = request.GET.get('loginId')
#     login_vo = LoginVO.objects.get(login_id=login_id)
#     login_vo.login_status = False
#     login_vo.save()
#     return redirect("/admin_view_user")
#
#
# @login_required('admin')
# def admin_unblock_user(request):
#     login_id = request.GET.get('loginId')
#     login_vo = LoginVO.objects.get(login_id=login_id)
#     login_vo.login_status = True
#     login_vo.save()
#     return redirect('/admin_view_user')
#
#
# def user_load_forget_password(request):
#     return render(request, 'user/forgetPassword.html')
#
#
# def user_validate_login_username(request):
#     login_username = request.POST.get("loginUsername")
#     login_vo_list = LoginVO.objects.filter(login_username=login_username)
#     login_list = [model_to_dict(i) for i in login_vo_list]
#     len_login_list = len(login_list)
#     if len_login_list == 0:
#         error_message = 'username is incorrect !'
#         messages.info(request, error_message)
#         return redirect('/user/load_forget_password')
#     else:
#         login_id = login_list[0]['login_id']
#         request.session['session_login_id'] = login_id
#         login_username = login_list[0]['login_username']
#         sender = "noreplypython@yahoo.com"
#         receiver = login_username
#         msg = MIMEMultipart()
#         msg['From'] = sender
#         msg['To'] = receiver
#         msg['Subject'] = "PYTHON OTP"
#         otp = random.randint(1000, 9999)
#         request.session['session_otp_number'] = otp
#         message = str(otp)
#         msg.attach(MIMEText(message, 'plain'))
#         server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
#         server.starttls()
#         server.login(sender, "dbzivjinwbndvvey")
#         text = msg.as_string()
#         server.sendmail(sender, receiver, text)
#         server.quit()
#         return render(request, 'user/otpValidation.html')
#
#
# def user_validate_otp_number(request):
#     otp_number = int(request.POST.get("otpNumber"))
#     session_otp_number = request.session.get('session_otp_number')
#     if otp_number == session_otp_number:
#         return render(request, 'user/resetPassword.html')
#     else:
#         request.session.flush()
#
#         error_message = 'otp is incorrect !'
#         messages.info(request, error_message)
#         return redirect('/user/load_forget_password')
#
#
# def user_insert_reset_password(request):
#     login_password = request.POST.get("loginPassword")
#     salt = bcrypt.gensalt(rounds=12)
#     hashed_login_password = bcrypt.hashpw(
#         login_password.encode(config.get("ALGORITHMS", "ENCODING")),
#         salt).decode(config.get("ALGORITHMS", "ENCODING"))
#     login_id = request.session.get("session_login_id")
#     login_vo = LoginVO.objects.get(login_id=login_id)
#     login_vo.login_password = hashed_login_password
#     login_vo.save()
#     return redirect('/')
