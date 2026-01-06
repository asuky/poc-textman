from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from blog.models import Category, Post, Comment, Tag

# ============================================================
# データベースシーディングコマンド
# ============================================================
# 実行方法: python manage.py seed_data
#
# このコマンドはテスト用のダミーデータをデータベースに投入します。
# 開発環境でのテストや動作確認に使用してください。
# ============================================================


class Command(BaseCommand):
    help = 'データベースにテストデータを投入します'
    
    def add_arguments(self, parser):
        """
        コマンドライン引数を追加
        
        --clear オプションで既存データを削除してから投入
        """
        parser.add_argument(
            '--clear',
            action='store_true',
            help='既存のブログデータを削除してから新規データを投入'
        )
    
    def handle(self, *args, **options):
        """
        コマンドの実行内容
        """
        # 既存データの削除
        if options['clear']:
            self.stdout.write(self.style.WARNING('既存データを削除中...'))
            Post.objects.all().delete()
            Category.objects.all().delete()
            Tag.objects.all().delete()
            Comment.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ 既存データを削除しました'))
        
        # ユーザーの作成または取得
        self.stdout.write('ユーザーを確認中...')
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ 管理者ユーザーを作成: {admin_user.username} (パスワード: admin123)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ 既存の管理者ユーザーを使用: {admin_user.username}'))
        
        # 通常ユーザーの作成
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@example.com',
            }
        )
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ デモユーザーを作成: {demo_user.username} (パスワード: demo123)'))
        
        # カテゴリの作成
        self.stdout.write('カテゴリを作成中...')
        categories_data = [
            {'name': 'Technology', 'description': '技術に関する記事'},
            {'name': 'Programming', 'description': 'プログラミングに関する記事'},
            {'name': 'Web Development', 'description': 'Web開発に関する記事'},
            {'name': 'Database', 'description': 'データベースに関する記事'},
            {'name': 'DevOps', 'description': 'DevOpsに関する記事'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
            status = '作成' if created else '既存'
            self.stdout.write(f'  - {status}: {category.name}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(categories)}個のカテゴリを用意しました'))
        
        # タグの作成
        self.stdout.write('タグを作成中...')
        tag_names = ['Python', 'Django', 'JavaScript', 'React', 'PostgreSQL', 'Docker', 'Git', 'API', 'Testing', 'Security']
        
        tags = []
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(tags)}個のタグを用意しました'))
        
        # 記事の作成
        self.stdout.write('記事を作成中...')
        posts_data = [
            {
                'title': 'Djangoでブログを作る方法',
                'slug': 'how-to-create-blog-with-django',
                'content': '''Djangoは強力なWebフレームワークです。この記事では、Djangoを使って簡単なブログアプリケーションを作成する方法を解説します。

まず、プロジェクトを作成します：
django-admin startproject myblog

次に、アプリケーションを作成します：
python manage.py startapp blog

モデルを定義し、マイグレーションを実行します。N+1問題を避けるために、select_related と prefetch_related を適切に使用することが重要です。''',
                'category': categories[1],  # Programming
                'tags': [tags[0], tags[1]],  # Python, Django
                'status': 'published',
                'author': admin_user,
            },
            {
                'title': 'データベースのN+1問題とその解決方法',
                'slug': 'database-n-plus-one-problem',
                'content': '''N+1問題は、ORMを使用する際に頻繁に発生するパフォーマンス問題です。

例えば、ブログの記事一覧を表示する際、各記事の著者名を表示しようとすると：
- 記事一覧取得: 1回のクエリ
- 各記事の著者取得: N回のクエリ（N = 記事数）

合計でN+1回のクエリが発行されてしまいます。

解決方法：
1. select_related() - 1対多、1対1の関係に使用
2. prefetch_related() - 多対多の関係に使用
3. only() / defer() - 必要なフィールドのみ取得

これらを適切に組み合わせることで、クエリ数を大幅に削減できます。''',
                'category': categories[3],  # Database
                'tags': [tags[1], tags[4]],  # Django, PostgreSQL
                'status': 'published',
                'author': admin_user,
            },
            {
                'title': 'Pythonでのテスト駆動開発（TDD）',
                'slug': 'python-test-driven-development',
                'content': '''テスト駆動開発（TDD）は、コードを書く前にテストを書く開発手法です。

TDDのサイクル：
1. Red - 失敗するテストを書く
2. Green - テストが通る最小限のコードを書く
3. Refactor - コードをリファクタリングする

Djangoでは、TestCaseクラスを使ってテストを書くことができます。モデルのテスト、ビューのテスト、APIのテストなど、様々なレベルでテストを書くことが重要です。''',
                'category': categories[1],  # Programming
                'tags': [tags[0], tags[8]],  # Python, Testing
                'status': 'published',
                'author': demo_user,
            },
            {
                'title': 'Dockerを使った開発環境の構築',
                'slug': 'docker-development-environment',
                'content': '''Dockerを使うことで、開発環境を簡単に構築・共有できます。

メリット：
- 環境の一貫性
- セットアップの簡略化
- 依存関係の管理

docker-compose.ymlを使って、アプリケーション、データベース、Redisなどを一括で起動できます。

本番環境でも同じDockerイメージを使用することで、開発環境と本番環境の差異を最小限に抑えられます。''',
                'category': categories[4],  # DevOps
                'tags': [tags[5], tags[6]],  # Docker, Git
                'status': 'published',
                'author': admin_user,
            },
            {
                'title': 'RESTful APIの設計ベストプラクティス',
                'slug': 'restful-api-best-practices',
                'content': '''RESTful APIを設計する際のベストプラクティスをまとめました。

1. リソース指向のURL設計
   - GET /api/posts/ - 記事一覧
   - POST /api/posts/ - 記事作成
   - GET /api/posts/{id}/ - 記事詳細
   - PUT /api/posts/{id}/ - 記事更新
   - DELETE /api/posts/{id}/ - 記事削除

2. 適切なHTTPステータスコードの使用
   - 200 OK - 成功
   - 201 Created - 作成成功
   - 400 Bad Request - クライアントエラー
   - 404 Not Found - リソースが見つからない
   - 500 Internal Server Error - サーバーエラー

3. バージョニング
   - /api/v1/posts/
   - ヘッダー: Accept: application/vnd.myapi.v1+json

4. ペジネーション、フィルタリング、ソート
   - ?page=2&limit=20
   - ?status=published
   - ?sort=-created_at''',
                'category': categories[2],  # Web Development
                'tags': [tags[7], tags[1]],  # API, Django
                'status': 'published',
                'author': admin_user,
            },
            {
                'title': 'セキュリティの基本 - SQLインジェクション対策',
                'slug': 'sql-injection-prevention',
                'content': '''SQLインジェクションは、最も一般的なセキュリティ脆弱性の一つです。

危険な例（決してやらないこと）：
query = f"SELECT * FROM users WHERE username = '{username}'"

安全な方法：
1. プレースホルダを使用
   cursor.execute("SELECT * FROM users WHERE username = %s", [username])

2. ORMを使用
   User.objects.filter(username=username)

DjangoのORMは、デフォルトでSQLインジェクション対策が施されています。生のSQLを使う必要がある場合は、必ずパラメータ化されたクエリを使用してください。

その他の対策：
- 入力値のバリデーション
- 最小権限の原則
- エラーメッセージの適切な処理''',
                'category': categories[3],  # Database
                'tags': [tags[9], tags[4]],  # Security, PostgreSQL
                'status': 'published',
                'author': demo_user,
            },
            {
                'title': '下書き：新機能の企画中',
                'slug': 'draft-new-feature',
                'content': '''この記事はまだ下書きです。新機能についての企画を進めています。''',
                'category': categories[0],  # Technology
                'tags': [tags[0]],  # Python
                'status': 'draft',
                'author': admin_user,
            },
        ]
        
        posts = []
        for post_data in posts_data:
            post_tags = post_data.pop('tags', [])
            
            post, created = Post.objects.get_or_create(
                slug=post_data['slug'],
                defaults={
                    **post_data,
                    'published_at': timezone.now() if post_data['status'] == 'published' else None
                }
            )
            
            # タグを追加
            if created and post_tags:
                post.tags.set(post_tags)
            
            posts.append(post)
            status = '作成' if created else '既存'
            self.stdout.write(f'  - {status}: {post.title}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(posts)}件の記事を用意しました'))
        
        # コメントの作成
        self.stdout.write('コメントを作成中...')
        comments_data = [
            {
                'post': posts[0],
                'author': demo_user,
                'content': 'とても参考になりました！Djangoでブログを作るのが楽しみです。',
            },
            {
                'post': posts[0],
                'author': admin_user,
                'content': 'ありがとうございます！何か質問があればお気軽にどうぞ。',
            },
            {
                'post': posts[1],
                'author': demo_user,
                'content': 'N+1問題について詳しく解説されていて助かりました。select_relatedとprefetch_relatedの使い分けが理解できました。',
            },
            {
                'post': posts[2],
                'author': admin_user,
                'content': 'TDDは最初は慣れないかもしれませんが、長期的にはコードの品質向上に繋がりますね。',
            },
            {
                'post': posts[4],
                'author': demo_user,
                'content': 'API設計のベストプラクティス、とても勉強になります！',
            },
        ]
        
        comment_count = 0
        for comment_data in comments_data:
            comment, created = Comment.objects.get_or_create(
                post=comment_data['post'],
                author=comment_data['author'],
                content=comment_data['content']
            )
            if created:
                comment_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {comment_count}件のコメントを作成しました'))
        
        # 完了メッセージ
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🎉 テストデータの投入が完了しました！'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write('作成されたデータ:')
        self.stdout.write(f'  - ユーザー: 2名（admin, demo）')
        self.stdout.write(f'  - カテゴリ: {len(categories)}個')
        self.stdout.write(f'  - タグ: {len(tags)}個')
        self.stdout.write(f'  - 記事: {len(posts)}件（公開: {len([p for p in posts if p.status == "published"])}件、下書き: {len([p for p in posts if p.status == "draft"])}件）')
        self.stdout.write(f'  - コメント: {comment_count}件')
        self.stdout.write('')
        self.stdout.write('ログイン情報:')
        self.stdout.write(f'  管理者: username=admin, password=admin123')
        self.stdout.write(f'  デモ: username=demo, password=demo123')
        self.stdout.write('')
        self.stdout.write('次のステップ:')
        self.stdout.write('  1. python manage.py runserver')
        self.stdout.write('  2. http://localhost:8000/blog/ にアクセス')
        self.stdout.write('  3. http://localhost:8000/admin/ で管理画面にログイン')
