import datetime
from datetime import date

import jwt
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from base.models import ComplainVO, UserVO, ReplyVO, LoginVO
from core.settings import SECRET_KEY
from .login_view import login_required


@never_cache
@login_required('user')
def user_send_complain(request):
    complain_vo = ComplainVO()
    login_id = request.session.get('login_id')
    user_list = UserVO.objects.get(user_login_vo=login_id)

    complain_vo.complain_subject = request.POST.get('complain_subject')
    complain_vo.complain_description = request.POST.get('complain_description')
    complain_vo.complain_date = date.today()
    complain_vo.complain_status = "Pending"
    complain_vo.complain_user_vo = user_list
    complain_vo.save()

    return render(request, "user/contact-us.html")


@never_cache
@login_required('admin')
def admin_view_complain(request):
    complain_vo_list = ComplainVO.objects.raw('''SELECT * FROM complain_table ct INNER JOIN login_table lt ON
    ct.complain_user_id =lt.login_id LEFT JOIN reply_table rt ON
    rt.reply_complain_id=ct.complain_id''')
    return render(request, 'admin/viewComplain.html',
                  context={'complain_vo_list': complain_vo_list})


@never_cache
@login_required('admin')
def admin_reply_complain(request):
    complain_id = request.GET.get('complainId')
    complain_vo_list = ComplainVO.objects.get(complain_id=complain_id)

    return render(request, 'admin/complaintReply.html',
                  context={"complain_vo_list": complain_vo_list})


@never_cache
@login_required('admin')
def admin_insert_complain_reply(request):
    complain_id = request.POST.get('complainId')
    reply_description = request.POST.get('complainReply')
    refreshtoken = request.COOKIES.get('refreshtoken')
    data = jwt.decode(refreshtoken, SECRET_KEY, 'HS256')

    reply_vo = ReplyVO()

    login_vo = LoginVO.objects.filter(
        login_username=data['public_id']).first()
    complain_vo = ComplainVO.objects.get(complain_id=complain_id)
    complain_vo.complain_status = "Replied"
    complain_vo.complain_id = complain_id
    print(complain_vo.complain_status, complain_vo.complain_id)
    complain_vo.save()

    reply_vo.reply_datetime = datetime.date.today()
    print("11111", reply_vo.reply_datetime)
    reply_vo.reply_description = reply_description
    reply_vo.reply_complain_vo = complain_vo
    reply_vo.reply_login_vo = login_vo
    reply_vo.save()
    print("!!!!!!!!!!!!!!!", reply_vo.reply_datetime,
          reply_vo.reply_description, reply_vo.reply_complain_vo)
    return redirect('/admin_view_complain')


@never_cache
@login_required('user')
def user_contact_us(request):
    login_id = request.session.get('login_id')
    login_vo = UserVO.objects.get(user_login_vo=login_id)
    complaint_vo_list = ComplainVO.objects \
        .select_related('complain_user_vo') \
        .filter(complain_user_vo=login_vo) \
        .all()
    reply_vo_list = ReplyVO.objects.select_related(
        'reply_complain_vo').select_related('reply_login_vo').all()
    print("111111", reply_vo_list)
    print("111111", complaint_vo_list)
    return render(request, "user/contact-us.html",
                  {'complaint_vo_list': complaint_vo_list, 'reply_vo_list': reply_vo_list})

# Create your views here.
#def admin_view_complain(request):
 #   return render(request, 'admin/viewComplain.html')
