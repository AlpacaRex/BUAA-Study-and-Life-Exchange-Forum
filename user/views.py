from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from post.models import *
from user.models import *
from django.http import JsonResponse


@csrf_exempt
def register(request):
    if request.method == 'POST':
        id = request.POST.get('id')
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
                if user.first_login:
                    user.first_login = False
                return JsonResponse({'errno': 0, 'msg': "登录成功", 'username': user.username})
            else:
                return JsonResponse({'errno': 2002, 'msg': "密码错误"})
        else:
            return JsonResponse({'errno': 2003, 'msg': "用户不存在"})
        pass
    else:
        return JsonResponse({'errno': 2001, 'msg': "请求方式错误"})


@csrf_exempt
def logout(request):
    request.session.flush()
    return JsonResponse({'errno': 0, 'msg': "注销成功"})


@csrf_exempt
def info(request):
    user_id = int(request.session.get('id', 0))
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
        if request.POST.get('security_issue'):
            user.security_issue = request.POST.get('security_issue')
        if request.POST.get('security_answer'):
            user.security_answer = request.POST.get('security_answer')
        if request.FILES.get('headshot'):
            user.headshot = request.FILES.get('headshot')
        user.save()
        return JsonResponse({'errno': 0, 'msg': "更改个人信息成功"})
    else:
        data = {
            'id': user.id,
            'username': user.username,
            'description': user.description,
            'level': user.level,
            'grade': user.grade,
            'major': user.major,
            'sex': user.sex,
            'password': user.password,
            'security_issue': user.security_issue,
            'security_answer': user.security_answer,
            'headshot': user.photo_url()
        }
        return JsonResponse({'errno': 0, 'data': data})


@csrf_exempt
def issue(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        if User.objects.filter(id=id).exists():
            user = User.objects.get(id=id)
            return JsonResponse({'errno': 0, 'security_issue': user.security_issue})
        else:
            return JsonResponse({'errno': 4002, 'msg': "用户不存在"})
    else:
        return JsonResponse({'errno': 4001, 'msg': "请求方式错误"})


@csrf_exempt
def password(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        if not User.objects.filter(id=id).exists():
            return JsonResponse({'errno': 5003, 'msg': "用户不存在"})
        user = User.objects.get(id=id)
        security_answer = request.POST.get('security_answer')
        if security_answer == user.security_answer:
            return JsonResponse({'errno': 0, 'password': user.password})
        else:
            return JsonResponse({'errno': 5002, 'msg': "答案错误"})
    else:
        return JsonResponse({'errno': 5001, 'msg': "请求方式错误"})


@csrf_exempt
def posted(request):
    if request.method == 'GET':
        user_id = request.session.get('id', 0)
        if user_id == 0:
            return JsonResponse({'errno': 9002, 'msg': "用户未登录"})
        user = User.objects.get(id=user_id)
        posts = []
        for x in Post.objects.filter(user=user):
            posts.append(x.to_dict())
        return JsonResponse({'errno': 0, 'posts': posts})
    else:
        return JsonResponse({'errno': 9001, 'msg': "请求方式错误"})


@csrf_exempt
def history(request):
    user_id = request.session.get('id', 0)
    if user_id == 0:
        return JsonResponse({'errno': 10001, 'msg': "用户未登录"})
    user = User.objects.get(id=user_id)
    if request.method == 'GET':
        posts = []
        for x in History.objects.filter(user=user):
            posts.append(Post.objects.get(id=x.post_id).to_dict())
        return JsonResponse({'errno': 0, 'posts': posts})
    elif request.method == 'POST':
        post_id = request.POST.get('post_id', 0)
        if post_id == 0:
            history = History.objects.filter(user=user)
            history.delete()
        else:
            if not Post.objects.filter(id=post_id):
                return JsonResponse({'errno': 10002, 'msg': "帖子不存在"})
            post = Post.objects.get(id=post_id)
            if not History.objects.filter(user=user, post=post).exists():
                return JsonResponse({'errno': 10003, 'msg': "历史记录不存在"})
            history = History.objects.get(user=user, post=post)
            history.delete()
        return JsonResponse({'errno':0, 'msg': "删除历史记录成功"})


@csrf_exempt
def favorites(request):
    user_id = request.session.get('id', 0)
    if user_id == 0:
        return JsonResponse({'errno': 11001, 'msg': "用户未登录"})
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        post_id = request.POST.get('post_id', 0)
        if post_id == 0:
            return JsonResponse({'errno': 11002, 'msg': "帖子ID不能为空"})
        if not Post.objects.filter(id=post_id).exists():
            return JsonResponse({'errno': 11003, 'msg': "帖子不存在"})
        post = Post.objects.get(id=post_id)
        op = int(request.POST.get('op', 0))
        if op == 0:
            if Favorites.objects.filter(user=user, post=post).exists():
                return JsonResponse({'errno': 11004, 'msg': "帖子已收藏"})
            Favorites.objects.create(user=user, post=post)
            return JsonResponse({'errno': 0, 'msg': "添加收藏夹成功"})
        else:
            if not Favorites.objects.filter(user=user, post=post).exists():
                return JsonResponse({'errno': 11005, 'msg': "帖子未收藏"})
            favorites = Favorites.objects.get(user=user, post=post)
            favorites.delete()
            return JsonResponse({'errno': 0, 'msg': "移除收藏夹成功"})
    else:
        posts = []
        for x in Favorites.objects.filter(user=user):
            posts.append(Post.objects.get(id=x.post_id).to_dict())
        return JsonResponse({'errno': 0, 'posts': posts})
