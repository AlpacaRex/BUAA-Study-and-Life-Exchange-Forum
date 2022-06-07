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
        if User.objects.filter(id=id).exists():
            user = User.objects.get(id=id)
            if user.password == password:
                request.session['id'] = id
                return JsonResponse({'errno': 0, 'msg': "登录成功", 'username': user.username})
            else:
                return JsonResponse({'errno': 2002, 'msg': "密码错误"})
        else:
            return JsonResponse({'errno': 2003, 'msg': "用户不存在"})
    else:
        return JsonResponse({'errno': 2001, 'msg': "请求方式错误"})


@csrf_exempt
def logout(request):
    request.session.flush()
    return JsonResponse({'errno': 0, 'msg': "注销成功"})


@csrf_exempt
def info(request):
    user_id = request.session.get('id', 0)
    print(user_id)
    if user_id == 0:
        return JsonResponse({'errno': 3001, 'msg': "用户未登录"})
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        if request.POST.get('username'):
            user.username = request.POST.get('username')
        if request.POST.get('description'):
            user.description = request.POST.get('description')
        if request.POST.get('grade'):
            user.grade = request.POST.get('grade')
        if request.POST.get('major'):
            user.major = request.POST.get('major')
        if request.POST.get('sex'):
            user.sex = request.POST.get('sex')
        if request.FILES.get('headshot'):
            user.headshot = request.FILES.get('headshot')
        user.save()
        return JsonResponse({'errno': 0, 'msg': "更改个人信息成功"})
    else:
        data = {
            'id': user.id,
            'username': user.username,
            'description': user.description,
            'grade': user.grade,
            'major': user.major,
            'sex': user.sex,
            'headshot': user.photo_url()
        }
        return JsonResponse({'errno': 0, 'data': data})


@csrf_exempt
def issue(request):
    if request.method == 'GET':
        id = int(request.GET.get('id'))
        user = User.objects.get(id=id)
        if user:
            return JsonResponse({'errno': 0, 'security_issue': user.security_issue})
        else:
            return JsonResponse({'errno': 4002, 'msg': "用户不存在"})
    else:
        return JsonResponse({'errno': 4001, 'msg': "请求方式错误"})


@csrf_exempt
def password(request):
    if request.method == 'POST':
        id = int(request.POST.get('id'))
        user = User.objects.get(id=id)
        security_answer = request.POST.get('security_answer')
        if security_answer == user.security_answer:
            return JsonResponse({'errno': 0, 'password': user.password})
        else:
            return JsonResponse({'errno': 5002, 'msg': "答案错误"})
    else:
        return JsonResponse({'errno': 5001, 'msg': "请求方式错误"})

