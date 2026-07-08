from django.shortcuts import render
from django.views.generic import ListView, DetailView
from base.models import Store, Category, Tag, Favorite
from django.db.models import Q

class StoreListView(ListView):
    model = Store
    template_name = 'pages/index.html'

    def get_queryset(self):
        #ベースとなる全件を取得
        queryset = super().get_queryset()
        #検索ワードを取得
        search_query = self.request.GET.get('q')
        #検索ワードが存在する場合はフィルタリング
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        return queryset

class StoreDetailView(DetailView):
    model = Store
    template_name = 'pages/store_detail.html'

    def get_context_data(self, **kwargs):
        # まず元々のコンテキスト（店舗データなど）を取得
        context = super().get_context_data(**kwargs)
        
        # ログインしていて、かつ有料会員（member）が存在する場合のみチェック
        if self.request.user.is_authenticated and getattr(self.request.user, 'member', None):
            # 現在表示している店舗（self.object）とログインユーザーがFavoriteテーブルに存在するか確認
            context['is_favorite'] = Favorite.objects.filter(
                member=self.request.user.member, 
                store=self.object
            ).exists()  # 存在すれば True、なければ False
        else:
            context['is_favorite'] = False
            
        return context