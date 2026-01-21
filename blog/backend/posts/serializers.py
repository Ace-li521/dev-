from rest_framework import serializers
from .models import Post, Comment
from users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'cover', 'author', 'created_at', 'comments', 'comment_count']

    def get_comment_count(self, obj):
        return obj.comments.count()


class PostListSerializer(serializers.ModelSerializer):
    """列表用，不含评论详情"""
    author = UserSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'cover', 'author', 'created_at', 'comment_count']

    def get_comment_count(self, obj):
        return obj.comments.count()
