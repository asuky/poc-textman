"""
Django REST Framework シリアライザー

============================================================
Serializerとは？
============================================================
Serializerは、DjangoのモデルとJSON/XMLなどの形式を相互変換し、
バリデーションも自動的に行ってくれるDRFの中核機能です。

主な役割：
1. モデル → JSON への変換（シリアライゼーション）
2. JSON → モデル への変換（デシリアライゼーション）
3. バリデーション（自動 + カスタム）
4. データの保存

公式ドキュメント:
https://www.django-rest-framework.org/api-guide/serializers/
https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
============================================================
"""

from rest_framework import serializers
from .models import Post, Category, Tag, Comment
import re


class TagSerializer(serializers.ModelSerializer):
    """
    タグのシリアライザー
    
    ModelSerializerを使うと、モデルの定義から自動的に
    フィールドとバリデーションを生成してくれます。
    """
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']  # 読み取り専用フィールド


class CategorySerializer(serializers.ModelSerializer):
    """カテゴリのシリアライザー"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['id', 'slug']


class PostListSerializer(serializers.ModelSerializer):
    """
    記事一覧用のシリアライザー
    
    一覧表示では詳細情報は不要なので、必要最小限のフィールドのみ返します。
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tag_names = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(read_only=True)  # annotateで追加される
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author_username', 
            'category_name', 'tag_names', 'comment_count',
            'status', 'created_at', 'published_at'
        ]
    
    def get_tag_names(self, obj):
        """タグ名のリストを返す"""
        return [tag.name for tag in obj.tags.all()]


class PostDetailSerializer(serializers.ModelSerializer):
    """
    記事詳細用のシリアライザー
    
    詳細表示では、関連するオブジェクトの情報も含めて返します。
    """
    author = serializers.CharField(source='author.username', read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'author', 
            'category', 'tags', 'status', 
            'created_at', 'updated_at', 'published_at'
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    """
    記事作成用のシリアライザー
    
    ============================================================
    カスタムバリデーション
    ============================================================
    
    1. フィールドレベルのバリデーション:
       - clean_<field_name>() メソッドで実装
       - 特定のフィールドだけをチェック
    
    2. オブジェクトレベルのバリデーション:
       - validate() メソッドで実装
       - 複数フィールドの組み合わせをチェック
    
    3. モデルレベルのバリデーション:
       - モデルの clean() メソッドで実装
       - is_valid() 時に自動的に呼ばれる
    
    公式ドキュメント:
    https://www.django-rest-framework.org/api-guide/serializers/#validation
    ============================================================
    """
    # タグは名前の配列で受け取る
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True,
        write_only=True  # 入力時のみ使用（出力には含まれない）
    )
    
    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'status', 'category', 'tag_names']
        extra_kwargs = {
            'status': {'default': 'draft'},  # デフォルト値
        }
    
    def validate_slug(self, value):
        """
        slugのカスタムバリデーション
        
        このメソッドは自動的に呼ばれます。
        フィールド名が 'slug' なので、メソッド名は 'validate_slug' です。
        """
        # 小文字英数字とハイフンのみ許可
        if not re.match(r'^[a-z0-9-]+$', value):
            raise serializers.ValidationError(
                'Slug can only contain lowercase letters, numbers, and hyphens'
            )
        
        # 重複チェック
        if Post.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                f'Post with slug "{value}" already exists'
            )
        
        return value
    
    def validate_title(self, value):
        """titleのバリデーション"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError('Title cannot be empty')
        return value.strip()
    
    def validate_content(self, value):
        """contentのバリデーション"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError('Content cannot be empty')
        return value.strip()
    
    def validate_status(self, value):
        """statusのバリデーション"""
        if value not in ['draft', 'published']:
            raise serializers.ValidationError(
                'Status must be either "draft" or "published"'
            )
        return value
    
    def create(self, validated_data):
        """
        記事を作成
        
        validated_data には、すべてのバリデーションを通過したデータが入ります。
        このメソッドで、実際にデータベースに保存する処理を実装します。
        """
        # tag_names を取り出す（モデルのフィールドではないため）
        tag_names = validated_data.pop('tag_names', [])
        
        # author は view 側で設定されるため、validated_data に含まれる
        post = Post.objects.create(**validated_data)
        
        # タグを追加
        for tag_name in tag_names:
            if tag_name.strip():
                tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
                post.tags.add(tag)
        
        return post
