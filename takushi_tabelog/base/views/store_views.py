from django.shortcuts import render
from django.views.generic import ListView, DetailView
from base.models import Store, Category, Tag
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