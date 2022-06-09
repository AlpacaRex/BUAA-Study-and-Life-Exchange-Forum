import datetime
import time

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.timezone import now
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
        elif user.banned:
            return JsonResponse({'errno': 6007, 'msg': "被禁言用户不能发帖"})
        post = Post()
        post.user = user
        post.title = request.POST.get('title')
        post.type = request.POST.get('type')
        if request.POST.get('available_level'):
            if int(request.POST.get('available_level')) > user.level:
                return JsonResponse({'errno': 6006, 'msg': "权限等级不能高于用户等级"})
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
        if user.level != 100:
            user.level += 3
            if user.level > 90:
                user.level = 90
            user.save()
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
        if user.banned:
            return JsonResponse({'errno': 7007, 'msg': "被禁言用户不能发表评论"})
        if post.available_level > user.level:
            return JsonResponse({'errno': 7006, 'msg': "用户等级不够"})
        comment = Comment()
        comment.post = post
        comment.user = user
        comment.floor = post.floor_num + 1
        post.floor_num += 1
        comment.content = request.POST.get('content')
        post.save()
        comment.save()
        if user.level != 100:
            user.level += 2
            if user.level > 90:
                user.level = 90
            user.save()
        user.save()
        return JsonResponse({'errno': 0, 'msg': "评论发布成功"})
    else:
        post_id = request.GET.get('post_id', 0)
        if post_id == 0:
            return JsonResponse({'errno': 7003, 'msg': "帖子ID不能为空"})
        if not Post.objects.filter(id=post_id).exists():
            return JsonResponse({'errno': 7005, 'msg': "帖子不存在"})
        post = Post.objects.get(id=post_id)
        if post.available_level > user.level:
            return JsonResponse({'errno': 7006, 'msg': "用户等级不够"})
        if History.objects.filter(user=user, post=post).exists():
            history = History.objects.get(user=user, post=post)
            history.browse_time = now()
            history.save()
        else:
            History.objects.create(user=user, post=post)
        comments = [{
            'id': x.id,
            'floor': x.floor,
            'comment_time': x.comment_time.strftime("%Y-%m-%d %H:%M:%S"),
            'content': x.content,
            'liked': LikedComment.objects.filter(user=user, comment=x).exists(),
            'user': User.objects.get(id=x.user.id).to_dict(),
        } for x in Comment.objects.filter(post=post)]
        post_dict = post.to_dict()
        post_dict['favorite'] = Favorites.objects.filter(user=user, post=post).exists()
        post_dict['liked'] = LikedPost.objects.filter(user=user, post=post).exists()
        return JsonResponse({'errno': 0, 'post': post_dict, 'comments': comments})


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


@csrf_exempt
def browse(request):
    if request.method == 'GET':
        posts = []
        type = request.GET.get('type')
        if type:
            if type == '最新':
                for x in Post.objects.all().order_by('-post_date')[0:10]:
                    posts.append(x.to_dict())
            else:
                for x in Post.objects.filter(type=type):
                    posts.append(x.to_dict())
        else:
            for x in Post.objects.all():
                posts.append(x.to_dict())
        return JsonResponse({'errno': 0, 'posts': posts})
    else:
        return JsonResponse({'errno': 12001, 'msg': "请求方式错误"})


@csrf_exempt
def like(request):
    if request.method == 'POST':
        user_id = request.session.get('id', 0)
        if user_id == 0:
            return JsonResponse({'errno': 13002, 'msg': "用户未登录"})
        user = User.objects.get(id=user_id)
        if request.POST.get('post_id'):
            post_id = request.POST.get('post_id')
            post = Post.objects.get(id=post_id)
            if LikedPost.objects.filter(user=user, post=post).exists():
                post_user = post.user
                post.likes -= 1
                post.save()
                liked_post = LikedPost.objects.get(user=user, post=post)
                liked_post.delete()
                return JsonResponse({'errno': 0, 'msg': "取消点赞成功"})
            else:
                post_user = post.user
                if post_user.level != 100:
                    post_user.level += 3
                    if post_user.level > 90:
                        post_user.level = 90
                    post_user.save()
                post.likes += 1
                post.save()
                LikedPost.objects.create(user=user, post=post)
                return JsonResponse({'errno': 0, 'msg': "点赞成功"})
        elif request.POST.get('comment_id'):
            comment_id = request.POST.get('comment_id')
            comment = Comment.objects.get(id=comment_id)
            if LikedComment.objects.filter(user=user, comment=comment).exists():
                comment.likes -= 1
                comment.save()
                liked_post = LikedComment.objects.get(user=user, comment=comment)
                liked_post.delete()
                return JsonResponse({'errno': 0, 'msg': "取消点赞成功"})
            else:
                comment.likes += 1
                comment.save()
                LikedComment.objects.create(user=user, comment=comment)
                return JsonResponse({'errno': 0, 'msg': "点赞成功"})
        else:
            return JsonResponse({'errno': 13003, 'msg': "帖子/评论ID不能为空"})
    else:
        return JsonResponse({'errno': 13001, 'msg': "请求方式错误"})


@csrf_exempt
def delete(request):
    if request.method == 'POST':
        user_id = request.session.get('id', 0)
        if user_id == 0:
            return JsonResponse({'errno': 14002, 'msg': "用户未登录"})
        user = User.objects.get(id=user_id)
        post_id = request.POST.get('post_id', 0)
        if post_id == 0:
            return JsonResponse({'errno': 14003, 'msg': "帖子ID不能为空"})
        if not Post.objects.filter(id=post_id).exists():
            return JsonResponse({'errno': 14004, 'msg': "帖子不存在"})
        post = Post.objects.get(id=post_id)
        if user != post.user and user.level < 100:
            return JsonResponse({'errno': 14005, 'msg': "无法删除别人发布的帖子"})
        post.delete()
        return JsonResponse({'errno': 0, 'msg': "删帖成功"})
    else:
        return JsonResponse({'errno': 14001, 'msg': "请求方式错误"})


@csrf_exempt
def report(request):
    user_id = request.session.get('id', 0)
    if user_id == 0:
        return JsonResponse({'errno': 15001, 'msg': "用户未登录"})
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        post_id = request.POST.get('post_id', 0)
        if post_id == 0:
            return JsonResponse({'errno': 15002, 'msg': "帖子ID不能为空"})
        if not Post.objects.filter(id=post_id).exists():
            return JsonResponse({'errno': 15003, 'msg': "帖子不存在"})
        post = Post.objects.get(id=post_id)
        post.report_times += 1
        post.save()
        return JsonResponse({'errno': 0, 'msg': "举报成功"})
    else:
        if user.level < 100:
            return JsonResponse({"errno": 15004, 'msg': "非管理员无法查看"})
        posts = []
        for x in Post.objects.all().order_by('-report_times'):
            if x.report_times > 0:
                posts.append(x.to_dict_report())
        return JsonResponse({'errno': 0, 'posts': posts})
