from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from user.models import *
from django.http import JsonResponse


@csrf_exempt
def register(request):
    if request.method == 'POST':
        id = int(request.POST.get('id'))
        username = request.POST.get('username')
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')
        security_issue = request.POST.get('security_issue')
        security_answer = request.POST.get('security_answer')
        users = User.objects.filter(id=id)
        if users.exists():
            return JsonResponse({'errno': 1002, 'msg': "该学号已注册"})
        if password_1 != password_2:
            return JsonResponse({'errno': 1003, 'msg': "两次输入的密码不一致"})
        User.objects.create(id=id, username=username, password=password_1, level=1, first_login=True, blockTime=0,
                            security_issue=security_issue, security_answer=security_answer)
        return JsonResponse({'errno': 0, 'msg': "成功"})
    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        password = request.POST.get('password')
        user = User.objects.get(id=id)
        if user.exists():
            if user.password == password:
                request.session['id'] = id
                return JsonResponse({'errno': 0, 'msg': "登录成功"})
            else:
                return JsonResponse({'errno': 2003, 'msg': "密码错误"})
        else:
            return JsonResponse({'errno': 2002, 'msg': "用户未注册"})
    else:
        return JsonResponse({'errno': 2001, 'msg': "请求方式错误"})


@csrf_exempt
def logout(request):
    request.session.flush()
    return JsonResponse({'errno': 0, 'msg': "注销成功"})
