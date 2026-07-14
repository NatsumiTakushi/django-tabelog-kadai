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
# ★ 作成した独立したファイルから、ピンポイントでクラスをインポートします
from base.views.reservation_views import ReservationCreateView
from base.views import ProfileUpdateView # ProfileUpdateViewをインポート
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
    # Account
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    # path('signup/', views.SignUpView.as_view()),
    # path('account/', views.AccountUpdateView.as_view()),
    path('profile/', ProfileUpdateView.as_view()),
    path('account/', ProfileUpdateView.as_view(), name='account'),
]
