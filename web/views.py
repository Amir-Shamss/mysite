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
#from postmark.core import PMMail


# Create your views here.


random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits))




def register(request):
    if request.POST.get('requestcode'):
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
            #message = PMMail(api_key = settings.POSTMark_API_TOKEN,
                             #subject = 'برای فعال سازی به لینک زیر مراجعه کنید http://www.hadirasool.tk/accounts/register?email={}&code={}'.format(email, code),
                             #sender = 'amir.shamss21@gmail.com',
                             #to = email,
                             #text_body = 'ایمیل تودو خود را در لینک زیر کلیک کنی',
                             #tag = 'create account')
            #message.send()
            context = {'message': 'لطفا پس از چک کردن ایمیل روی لینک زیر کلیک کنید'}
            return render(request, 'login.html', context)
        else:
            context = {'message','از نام کاربری دیگری استفاده کنید.ببخشید که فرم ذخیره نشده.درست میشه'}
            return render(request, 'register.html', context)
    elif request.GET.get('code'):
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




"""
<#captcha images#>


def captcha_image(request, key, scale=1):
    try:
        store = CaptchaStore.objects.get(hashkey=key)
    except CaptchaStore.DoesNotExist:
        # HTTP 410 Gone status so that crawlers don't index these expired urls.
        return HttpResponse(status=410)

    text = store.challenge

    if isinstance(settings.CAPTCHA_FONT_PATH, six.string_types):
        fontpath = settings.CAPTCHA_FONT_PATH
    elif isinstance(settings.CAPTCHA_FONT_PATH, (list, tuple)):
        fontpath = random.choice(settings.CAPTCHA_FONT_PATH)
    else:
        raise ImproperlyConfigured('settings.CAPTCHA_FONT_PATH needs to be a path to a font or list of paths to fonts')

    if fontpath.lower().strip().endswith('ttf'):
        font = ImageFont.truetype(fontpath, settings.CAPTCHA_FONT_SIZE * scale)
    else:
        font = ImageFont.load(fontpath)

    if settings.CAPTCHA_IMAGE_SIZE:
        size = settings.CAPTCHA_IMAGE_SIZE
    else:
        size = getsize(font, text)
        size = (size[0] * 2, int(size[1] * 1.4))

    image = makeimg(size)
    xpos = 2

    charlist = []
    for char in text:
        if char in settings.CAPTCHA_PUNCTUATION and len(charlist) >= 1:
            charlist[-1] += char
        else:
            charlist.append(char)
    for char in charlist:
        fgimage = Image.new('RGB', size, settings.CAPTCHA_FOREGROUND_COLOR)
        charimage = Image.new('L', getsize(font, ' %s ' % char), '#000000')
        chardraw = ImageDraw.Draw(charimage)
        chardraw.text((0, 0), ' %s ' % char, font=font, fill='#ffffff')
        if settings.CAPTCHA_LETTER_ROTATION:
            charimage = charimage.rotate(random.randrange(*settings.CAPTCHA_LETTER_ROTATION), expand=0, resample=Image.BICUBIC)
        charimage = charimage.crop(charimage.getbbox())
        maskimage = Image.new('L', size)

        maskimage.paste(charimage, (xpos, DISTANCE_FROM_TOP, xpos + charimage.size[0], DISTANCE_FROM_TOP + charimage.size[1]))
        size = maskimage.size
        image = Image.composite(fgimage, image, maskimage)
        xpos = xpos + 2 + charimage.size[0]

    if settings.CAPTCHA_IMAGE_SIZE:
        # centering captcha on the image
        tmpimg = makeimg(size)
        tmpimg.paste(image, (int((size[0] - xpos) / 2), int((size[1] - charimage.size[1]) / 2 - DISTANCE_FROM_TOP)))
        image = tmpimg.crop((0, 0, size[0], size[1]))
    else:
        image = image.crop((0, 0, xpos + 1, size[1]))
    draw = ImageDraw.Draw(image)

    for f in settings.noise_functions():
        draw = f(draw, image)
    for f in settings.filter_functions():
        image = f(image)

    out = StringIO()
    image.save(out, "PNG")
    out.seek(0)

    response = HttpResponse(content_type='image/png')
    response.write(out.read())
    response['Content-length'] = out.tell()

    return response

    """