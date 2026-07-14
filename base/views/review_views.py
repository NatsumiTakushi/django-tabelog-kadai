from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from base.models import Store, Review

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    template_name = 'pages/review.html'
    fields = ['rating', 'comment']

    def dispatch(self, request, *args, **kwargs):
        if not getattr(request.user, 'member', None) or not request.user.member.premium_member:
            raise PermissionDenied("レビューの投稿には有料会員登録が必要です。")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # 🌟 store_pk から pk に変更
        store_pk = self.kwargs.get('pk') 
        form.instance.store = get_object_or_404(Store, pk=store_pk)
        form.instance.member = self.request.user.member
        return super().form_valid(form)

    def get_success_url(self):
        # 🌟 store_pk から pk に変更
        return reverse_lazy('store_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 🌟 store_pk から pk に変更
        context['store'] = get_object_or_404(Store, pk=self.kwargs['pk'])
        return context

class MyReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'pages/my_reviews.html'  # テンプレートのパス
    context_object_name = 'reviews'         # テンプレート側で使う変数名

    def dispatch(self, request, *args, **kwargs):
        # 有料会員（プレミアム会員）かどうかのチェック
        if not getattr(request.user, 'member', None) or not request.user.member.premium_member:
            raise PermissionDenied("この機能の利用には有料会員登録が必要です。")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # ログインしている自分のmemberに紐づくレビューだけを取得し、新しい順（-created_at）に並べる
        return Review.objects.filter(member=self.request.user.member).order_by('-created_at')