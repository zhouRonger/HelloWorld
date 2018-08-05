from django.shortcuts import render,redirect
from .models import User,ConfirmString
from .forms import UserForm,RegisterForm
from django.conf import settings
import hashlib
import datetime

# Create your views here.

def send_email(email,code):
    from django.core.mail import EmailMultiAlternatives

    subject = '来自。。。。'
    text_content = '感谢。。。。'
    html_content = '''<p>感谢注册<a href = "http://{}/confirm/?code={}" target=blank>www.biadu.com</a>,\
                   这里是。。。。。</p>
                      <p>请点击。。。。</p>
                      <p>此链接有效期为{}天</p>'''.format('127.0.0.1:8000',code,settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject,text_content,settings.EMAIL_HOST_USER,[email])
    msg.attach_alternative(html_content,'text/html')
    msg.send()

def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name,now)
    ConfirmString.objects.create(code=code,user=user,)
    return code



def hash_code(s,salt="mysite"):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

def index(request):
    pass
    return render(request,"register/index.html")

def login(request):
    """if request.method == "POST":
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        if username and password:
            username.strip()
            try:
                user=User.objects.get(name = username)
                if password == user.password:
                    return redirect('/index/')
                else:
                    message = "密码不正确!"
            except:
                message = "用户名不存在!"
        return render(request,'register/login.html',{"message":message})
    return render(request,'register/login.html')"""
    if request.session.get('is_login',None):
        return redirect("/index/")
    if request.method == "POST":
        login_form = UserForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(name = username)
                if not user.has_confirmed:
                    message = "该用户还未通过邮件确认"
                    return render(request,'register/login.html',locals())
                if user.password == hash_code(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确!"
            except:
                message = "用户名不存在!"
        return render(request,'register/login.html',locals())
    login_form = UserForm()
    return render(request,'register/login.html',locals())

def register(request):
    """if request.session.get('is_login',None):
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if  password1 != password2:
                message = "两次输入密码不相同！"
                return render(request,'register/register.html',locals())
            else:
                same_name_user = User.objects.filter(name = username)
                if same_name_user :
                    message = "用户名已存在，请换个用户名!"
                    return render(request,"register/register.html",locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:
                    message = "邮箱已存在，请换一个邮箱!"
                    return render(request,'register/register.html',locals())

                new_user = User()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                return redirect('/login/')
    register_form = RegisterForm()
    return render(request,'register/register.html',locals())"""
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:
                message = "两次输入的密码不同！"
                return render(request, 'register/register.html', locals())
            length = int(len(password1))
            if  length < 8 or length > 14:
                message = "密码长度为8-14位"
                return render(request, 'register/register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'register/register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'register/register.html', locals())

                new_user = User(
                    name=username,
                    password=hash_code(password1),
                    email=email,
                    sex=sex,
                )
                new_user.save()
                """new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()"""

                code = make_confirm_string(new_user)
                send_email(email,code)
                message = "请前往注册邮箱，进行邮件确认!"
                return render(request,'register/confirm.html',locals())
    register_form = RegisterForm()
    return render(request, 'register/register.html', locals())



def logout(request):
    if not request.session.get('is_login',None):
        return redirect("/index/")
    request.session.flush()
    return redirect("/index/")

def user_confirm(request):
    code = request.GET.get('code',None)
    message=''
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        message='无效的确认请求!'
        return render(request,'login/confirm.html',locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()

    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已过期！请重新注册'
        return render(request,'register/confirm.html',locals())
    else:
        confirm.user.has_confirmed=True
        confirm.user.save()
        confirm.delete()
        message = "感谢确认。。"
        return render(request,'register/confirm.html',locals())