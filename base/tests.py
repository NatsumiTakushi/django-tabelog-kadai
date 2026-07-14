from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from base.models import Category, Tag, Member, PremiumMember
from django.utils import timezone
from datetime import timedelta

class CategoryTagAdminTests(TestCase):
    def setUp(self):
        # 管理者ユーザーを作成
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        # 一般ユーザーを作成
        self.normal_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='password123'
        )

    def test_category_list_and_create_by_admin(self):
        # 管理者でログイン
        self.client.login(username='admin', password='password123')
        
        # 1. 一覧表示（GET）
        response = self.client.get(reverse('admin_category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_pages/categories/list.html')
        
        # 2. 追加処理（POST）
        post_data = {
            'slug': 'test-cat',
            'name': 'テストカテゴリ'
        }
        response = self.client.post(reverse('admin_category_list'), post_data)
        self.assertRedirects(response, reverse('admin_category_list'))
        
        # 3. 追加後のデータ確認
        self.assertTrue(Category.objects.filter(slug='test-cat').exists())
        self.assertEqual(Category.objects.get(slug='test-cat').name, 'テストカテゴリ')

    def test_category_create_validation_error(self):
        self.client.login(username='admin', password='password123')
        
        # 無効なslug（特殊文字）
        post_data = {
            'slug': 'invalid@slug',
            'name': '無効なカテゴリ'
        }
        response = self.client.post(reverse('admin_category_list'), post_data)
        self.assertEqual(response.status_code, 200) # リダイレクトせず再描画
        self.assertFalse(Category.objects.filter(name='無効なカテゴリ').exists())
        # フォームにエラーメッセージが含まれていることを検証
        form = response.context['form']
        self.assertTrue(form.has_error('slug'))

    def test_category_delete_by_admin(self):
        # テストデータの作成
        cat = Category.objects.create(slug='temp-cat', name='一時カテゴリ')
        self.client.login(username='admin', password='password123')
        
        # 1. 削除確認画面（GET）
        response = self.client.get(reverse('admin_category_delete', kwargs={'pk': cat.slug}))
        self.assertEqual(response.status_code, 200)
        
        # 2. 削除処理（POST）
        response = self.client.post(reverse('admin_category_delete', kwargs={'pk': cat.slug}))
        self.assertRedirects(response, reverse('admin_category_list'))
        self.assertFalse(Category.objects.filter(slug='temp-cat').exists())

    def test_normal_user_cannot_access_categories(self):
        # 一般ユーザーでログイン
        self.client.login(username='user', password='password123')
        response = self.client.get(reverse('admin_category_list'))
        self.assertEqual(response.status_code, 403) # UserPassesTestMixin により 403 Forbidden が返る
        
    def test_tag_list_and_create_by_admin(self):
        self.client.login(username='admin', password='password123')
        
        # 1. 一覧表示（GET）
        response = self.client.get(reverse('admin_tag_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_pages/tags/list.html')
        
        # 2. 追加処理（POST）
        post_data = {
            'slug': 'test-tag',
            'name': 'テストタグ'
        }
        response = self.client.post(reverse('admin_tag_list'), post_data)
        self.assertRedirects(response, reverse('admin_tag_list'))
        
        # 3. 追加後のデータ確認
        self.assertTrue(Tag.objects.filter(slug='test-tag').exists())
        self.assertEqual(Tag.objects.get(slug='test-tag').name, 'テストタグ')

    def test_tag_delete_by_admin(self):
        tag = Tag.objects.create(slug='temp-tag', name='一時タグ')
        self.client.login(username='admin', password='password123')
        
        response = self.client.post(reverse('admin_tag_delete', kwargs={'pk': tag.slug}))
        self.assertRedirects(response, reverse('admin_tag_list'))
        self.assertFalse(Tag.objects.filter(slug='temp-tag').exists())

class AdminDashboardTests(TestCase):
    def setUp(self):
        # 管理者ユーザーを作成
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        
        # 一般ユーザー（会員）を作成し、そのうち2名をプレミアム会員にする
        self.user1 = User.objects.create_user(username='member1', email='m1@example.com', password='password123')
        self.member1 = Member.objects.create(user=self.user1, phone_number='111', address='Tokyo')
        
        self.user2 = User.objects.create_user(username='member2', email='m2@example.com', password='password123')
        self.member2 = Member.objects.create(user=self.user2, phone_number='222', address='Osaka')
        
        self.user3 = User.objects.create_user(username='member3', email='m3@example.com', password='password123')
        self.member3 = Member.objects.create(user=self.user3, phone_number='333', address='Kyoto')

        # member1 と member2 をプレミアム会員（有効期間内）にする
        now = timezone.now()
        PremiumMember.objects.create(member=self.member1, premium_expiration_date=now + timedelta(days=30))
        PremiumMember.objects.create(member=self.member2, premium_expiration_date=now + timedelta(days=10))

        # member3 は期限切れのプレミアム会員にする
        PremiumMember.objects.create(member=self.member3, premium_expiration_date=now - timedelta(days=1))

    def test_dashboard_shows_correct_metrics(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_pages/dashboard/report.html')
        
        # コンテキストデータの検証
        # アクティブな会員は member1 と member2 の2名（member3 は期限切れ）
        self.assertEqual(response.context['total_premium_members'], 2)
        self.assertEqual(response.context['sales_this_month'], 600)
        
        # HTMLレスポンスの検証
        self.assertContains(response, '2 名')
        self.assertContains(response, '¥600')
