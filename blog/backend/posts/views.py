import uuid
import oss2
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Post, Comment, Like
from .serializers import PostSerializer, PostListSerializer, CommentSerializer, LikeSerializer


class PostListView(APIView):
    """文章列表 / 创建文章"""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """文章详情 / 更新 / 删除"""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            return Response(PostSerializer(post).data)
        except Post.DoesNotExist:
            return Response({'error': '文章不存在'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, author=request.user)
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error': '无权限或文章不存在'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, author=request.user)
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'error': '无权限或文章不存在'}, status=status.HTTP_404_NOT_FOUND)


class CommentView(APIView):
    """评论"""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            content = request.data.get('content')
            if not content:
                return Response({'error': '评论内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            comment = Comment.objects.create(
                content=content,
                post=post,
                author=request.user
            )
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({'error': '文章不存在'}, status=status.HTTP_404_NOT_FOUND)


class UploadImageView(APIView):
    """上传图片到 OSS"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '请选择文件'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            return Response({'error': '只支持 jpg/png/gif/webp 格式'}, status=status.HTTP_400_BAD_REQUEST)

        # 生成唯一文件名
        ext = file.name.split('.')[-1]
        filename = f"blog/images/{uuid.uuid4().hex}.{ext}"

        try:
            # 上传到 OSS
            auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
            bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
            bucket.put_object(filename, file.read())

            # 返回图片 URL
            url = f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{filename}"
            return Response({'url': url})
        except Exception as e:
            return Response({'error': f'上传失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostLikeView(APIView):
    """文章点赞/取消点赞"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if not created:
                # 已点赞，取消点赞
                like.delete()
                return Response({'liked': False, 'like_count': post.likes.count()})
            return Response({'liked': True, 'like_count': post.likes.count()}, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({'error': '文章不存在'}, status=status.HTTP_404_NOT_FOUND)


class CommentLikeView(APIView):
    """评论点赞/取消点赞"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            like, created = Like.objects.get_or_create(user=request.user, comment=comment)
            if not created:
                like.delete()
                return Response({'liked': False, 'like_count': comment.likes.count()})
            return Response({'liked': True, 'like_count': comment.likes.count()}, status=status.HTTP_201_CREATED)
        except Comment.DoesNotExist:
            return Response({'error': '评论不存在'}, status=status.HTTP_404_NOT_FOUND)
