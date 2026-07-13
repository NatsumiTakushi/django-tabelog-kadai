"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from base import views
from django.contrib.auth.views import LoginView, LogoutView
from base.views.reservation_views import ReservationCreateView, ReservationCancelView
from base.views import ProfileUpdateView
from base.views.review_views import ReviewCreateView, MyReviewListView
from base.views.favorite_views import FavoriteToggleView, MyFavoriteListView
from base.views.premium_views import CreateCheckoutSessionView, PremiumSuccessView, PremiumCancelView, StripeWebhookView, WithdrawPremiumView
from base.views.account_views import DeleteAccountView
from django.views.generic import TemplateView
# 運営側インポート
from base.admin_views.dashboard_views import AdminDashboardView
from base.admin_views.store_views import (
    AdminStoreListView,
    AdminStoreCreateView,
    AdminStoreUpdateView,
    AdminStoreDeleteView
)
from base.admin_views.member_views import AdminMemberListView
from base.admin_views.category_views import AdminCategoryListView, AdminCategoryDeleteView
from base.admin_views.tag_views import AdminTagListView, AdminTagDeleteView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.StoreListView.as_view(), name='home'),
    # store detail view
    path('store/<str:pk>/', views.StoreDetailView.as_view(), name='store_detail'),
    # reservation 
    path(
        "store/<str:pk>/reservation/",
        ReservationCreateView.as_view(),
        name="reservation_form",
    ),
    path('reservation/<int:pk>/cancel/', ReservationCancelView.as_view(), name='reservation_cancel'),
    # Account
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view()),
    # path('signup/', views.SignUpView.as_view()),
    # path('account/', views.AccountUpdateView.as_view()),
    path('profile/', ProfileUpdateView.as_view()),
    path('account/', ProfileUpdateView.as_view(), name='account'),
    path('store/<str:pk>/review/', ReviewCreateView.as_view(), name='review_create'),
    # 自分が投稿したレビュー一覧画面
    path('my-reviews/', MyReviewListView.as_view(), name='my_reviews'),
    path('store/<str:pk>/favorite/', FavoriteToggleView.as_view(), name='favorite_toggle'),
    path('my-favorites/', MyFavoriteListView.as_view(), name='my_favorites'),
    path('premium/checkout/', CreateCheckoutSessionView.as_view(), name='premium_checkout'),
    path('premium/success/', PremiumSuccessView.as_view(), name='premium_success'),
    path('premium/cancel/', PremiumCancelView.as_view(), name='premium_cancel'),
    # 運営側専用のダッシュボードURL
    path('admin-panel/', AdminDashboardView.as_view(), name='admin_dashboard'),
    # 運営側専用の店舗一覧URL
    path('admin-panel/stores/', AdminStoreListView.as_view(), name='admin_store_list'),
    path('admin-panel/stores/create/', AdminStoreCreateView.as_view(), name='admin_store_create'),
    path('admin-panel/stores/<str:pk>/update/', AdminStoreUpdateView.as_view(), name='admin_store_update'),
    path('admin-panel/stores/<str:pk>/delete/', AdminStoreDeleteView.as_view(), name='admin_store_delete'),
    # 運営側専用の会員一覧URL
    path('admin-panel/members/', AdminMemberListView.as_view(), name='admin_member_list'),
    # 運営側専用のカテゴリ管理URL
    path('admin-panel/categories/', AdminCategoryListView.as_view(), name='admin_category_list'),
    path('admin-panel/categories/<str:pk>/delete/', AdminCategoryDeleteView.as_view(), name='admin_category_delete'),
    # 運営側専用のタグ管理URL
    path('admin-panel/tags/', AdminTagListView.as_view(), name='admin_tag_list'),
    path('admin-panel/tags/<str:pk>/delete/', AdminTagDeleteView.as_view(), name='admin_tag_delete'),
    # Webhook
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
    # 有料会員解約（premium_viewsから呼び出し）
    path('premium/withdraw/', WithdrawPremiumView.as_view(), name='premium_cancel_subscription'),
    # 退会手続き（account_viewsから呼び出し）
    path('account/delete/', DeleteAccountView.as_view(), name='account_delete'),
    path(
        "company/",
        TemplateView.as_view(template_name="pages/company.html"),
        name="company",
    ),
    path(
        "terms/",
        TemplateView.as_view(template_name="pages/terms.html"),
        name="terms",
    ),
    path(
        "privacy/",
        TemplateView.as_view(template_name="pages/privacy.html"),
        name="privacy",
    ),
]
