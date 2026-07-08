from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
from base.models import Store, Favorite

class FavoriteToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # 1. 有料会員（プレミアム会員）かどうかのチェック
        if not getattr(request.user, 'member', None) or not request.user.member.premium_member:
            raise PermissionDenied("お気に入り機能の利用には有料会員登録が必要です。")
        
        # 2. 対象の店舗を取得（ランダム文字列のIDに対応）
        store = get_object_or_404(Store, pk=self.kwargs['pk'])
        member = request.user.member

        # 3. すでにお気に入り登録されているか確認（トグル処理）
        favorite_queryset = Favorite.objects.filter(member=member, store=store)

        if favorite_queryset.exists():
            # すでに存在する場合は「お気に入り解除」
            favorite_queryset.delete()
        else:
            # 存在しない場合は「お気に入り追加」
            Favorite.objects.create(member=member, store=store)

        # 4. 元の店舗詳細画面にリダイレクトする
        return redirect('store_detail', pk=store.pk)

class MyFavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'pages/my_favorites.html'  # テンプレートファイル名
    context_object_name = 'favorites'         # テンプレートで使う変数名
    
    def get_queryset(self):
        # ログインしている会員のお気に入りを、新しい順（-created_at）に取得
        return Favorite.objects.filter(
            member=self.request.user.member
        ).order_by('-created_at')