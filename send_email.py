import os
from django.core.mail import EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE'] = 'Login.Login.settings'

if __name__ == '__main__':
    subject = '来自。。。。'
    text_context = '欢迎访问。。。'
    from_email = "1527099817@qq.com"
    to = 'byzhizi@126.com'
    html_content = '<p>欢迎访问<a href = "http://www.baidu.com" target=blank>www.liujiangblog.com</a>,这里是...，专注于。。。。</p>'
    h = EmailMultiAlternatives(subject,text_context,from_email,[to])
    h.attach_alternative(html_content,"text/html")
    h.send()