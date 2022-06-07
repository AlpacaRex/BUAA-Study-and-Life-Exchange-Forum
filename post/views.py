from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from post.models import *
from user.models import *


@csrf_exempt
def new(request):
    if request.method == 'POST':
        user_id = request.session.get('id', 0)
        if user_id == 0:
            return JsonResponse({'errno': 6002, 'msg': "用户未登录"})
        user = User.objects.get(id=user_id)
        if not request.POST.get('title'):
            return JsonResponse({'errno': 6003, 'msg': "标题不能为空"})
        elif not request.POST.get('type'):
            return JsonResponse({'errno': 6004, 'msg': "类型不能为空"})
        elif not request.POST.get('content'):
            return JsonResponse({'errno': 6005, 'msg': "内容不能为空"})
        post = Post()
        post.user = user
        post.title = request.POST.get('title')
        post.type = request.POST.get('type')
        if request.POST.get('available_level'):
            post.available_level = request.POST.get('available_level')
        post.save()
        if request.FILES.get('resource'):
            post.resource = request.FILES.get('resource')
        post.save()
        comment = Comment()
        comment.post = post
        comment.user = user
        comment.floor = 1
        comment.content = request.POST.get('content')
        comment.save()
        return JsonResponse({'errno': 0, 'msg': "新帖发布成功"})
    else:
        return JsonResponse({'errno': 6001, 'msg': "请求方式错误"})


@csrf_exempt
def comment(request):
    user_id = request.session.get('id', 0)
    if user_id == 0:
        return JsonResponse({'errno': 7002, 'msg': "用户未登录"})
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        post_id = request.POST.get('post_id', 0)
        if post_id == 0:
            return JsonResponse({'errno': 7003, 'msg': "帖子ID不能为空"})
        elif not request.POST.get('content'):
            return JsonResponse({'errno': 7004, 'msg': "内容不能为空"})
        if not Post.objects.filter(id=post_id).exists():
            return JsonResponse({'errno': 7005, 'msg': "帖子不存在"})
        post = Post.objects.get(id=post_id)
        comment = Comment()
        comment.post = post
        comment.user = user
        comment.floor = post.floor_num + 1
        post.floor_num += 1
        comment.content = request.POST.get('content')
        post.save()
        comment.save()
        return JsonResponse({'errno': 0, 'msg': "评论发布成功"})
    else:
        post_id = request.GET.get('post_id', 0)
        if post_id == 0:
            return JsonResponse({'errno': 7003, 'msg': "帖子ID不能为空"})
        if not Post.objects.filter(id=post_id).exists():
            return JsonResponse({'errno': 7005, 'msg': "帖子不存在"})
        post = Post.objects.get(id=post_id)
        comments = [{
            'floor': x.floor,
            'comment_time': x.comment_time,
            'content': x.content,
            'user': User.objects.get(id=x.user.id).to_dict(),
        } for x in Comment.objects.filter(post=post)]
        return JsonResponse({'errno': 0, 'post': post.to_dict(), 'comments': comments})


@csrf_exempt
def search(request):
    user_id = request.session.get('id', 0)
    if user_id == 0:
        return JsonResponse({'errno': 8002, 'msg': "用户未登录"})
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        if not keyword:
            return JsonResponse({'errno': 8003, 'msg': "搜索关键字不能为空"})
        posts = []
        for x in Post.objects.filter(title__icontains=keyword):
            posts.append(x.to_dict())
        return JsonResponse({'errno': 0, 'posts': posts})
    else:
        return JsonResponse({'errno': 8001, 'msg': "请求方式错误"})

