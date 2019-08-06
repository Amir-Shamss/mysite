# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from web.models import User, Token, Expense, Income
from datetime import datetime
from django.contrib.auth.hashers import make_password
import random
import string
import time
import  os
from postmark import PMMail


# Create your views here.


random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits))




def register(request):
    if request.POST.has_key('requestcode'):
        if not grecapcha_verify(request):
            context = {'message', 'سلام کد یا کلید یا تشخیص عکس زیر درست پر کنید ببخشید که فرم به شکل اولیه برنگشته'}
            return render(request, 'register.html', context)

        if User.objects.filter(email = request.POST['email']).exists():
            context = {'message', 'ببخشید که فرم ذخیره نمیشه درست میشه'}
            return render(request, 'register.html', context)

        if User.objects.filter(username = request.POST['username']).exists():
            code = random_str(28)
            now = datetime.now()
            email = request.POST['email']
            password = make_password(request.POST['password'])
            username = request.POST['username']
            temporarycode = Passwordresetcodes(email = email, time = now, code = code ,username = username, password = password)
            temporarycode.save()
            message = PMMail(api_key = settings.POSTMark_API_TOKEN,
                             subject = 'برای فعال سازی به لینک زیر مراجعه کنید http://www.hadirasool.tk/accounts/register?email={}&code={}'.format(email, code),
                             sender = 'amir.shamss21@gmail.com',
                             to = email,
                             text_body = 'ایمیل تودو خود را در لینک زیر کلیک کنی',
                             tag = 'create account')
            message.send()
            context = {'message': 'لطفا پس از چک کردن ایمیل روی لینک زیر کلیک کنید'}
            return render(request, 'login.html', context)
        else:
            context = {'message','از نام کاربری دیگری استفاده کنید.ببخشید که فرم ذخیره نشده.درست میشه'}
            return render(request, 'register.html', context)
    elif request.GET.has_key('code'):
        email = request.GET['email']
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(code=code).exists():
            new_temp_user = Passwordresetcodes.objects.get(code=code)
            newuser = User.objects.create(username=new_temp_user.username, password=new_temp_user.password, email=email)
            this_token = random_str(48)
            token = Token.objects.create(user=newuser, token=this_token)
            Passwordresetcodes.objects.filter(code=code).delete()
            context = {'message', 'اکانت شما فعال شد توکن شما {} است آن را ذخیره کنید چون نمایش داده نخواهد شد'.format(this_token)}
            return render(request, 'login.html', context)
        else:
            context = {'message', 'فعال سازی معتبر نیست در صورت نیاز دبار تلاش کنید'}
            return render(request, 'login.html', context)
    else:
        context = {'message': ''}
        return render(request, 'register.html', context)






@csrf_exempt
def submit_income(request):
    #print request.POST

    this_token=request.POST['token']
    this_user = User.objects.filter(token__token=this_token).get()
    if 'date' not in request.POST:
        date = datetime.now()
    Income.objects.create(user=this_user, amount=request.POST['amount'],text=request.POST['text'], date=datetime.now())
    return JsonResponse({
        'status':'ok' ,

    }, encoder=JSONEncoder)



@csrf_exempt
def submit_expense(request):
    #print request.POST

    this_token=request.POST['token']
    this_user = User.objects.filter(token__token=this_token).get()
    if 'date' not in request.POST:
        date = datetime.now()
    Expense.objects.create(user=this_user, amount=request.POST['amount'],text=request.POST['text'], date=datetime.now())
    return JsonResponse({
        'status':'ok' ,

    }, encoder=JSONEncoder)
