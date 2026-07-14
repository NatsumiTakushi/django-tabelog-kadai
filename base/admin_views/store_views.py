from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy
from base.models import Store  # ※Storeモデルの名前が異なる場合は適宜修正してください

class AdminStoreListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Store
    template_name = 'admin_pages/stores/list.html'
    context_object_name = 'stores'
    paginate_by = 10  # 1ページに10件表示

    # 運営者しか見られないように制限
    def is_staff_user(self):
        return self.request.user.is_staff

    def test_func(self):
        return self.is_staff_user()

    # 検索機能の追加
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            # 店舗名、または住所にキーワードが含まれるものを検索
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(address__icontains=query)
            )
        return queryset.order_by('-id')

class AdminStoreCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Store
    template_name = 'admin_pages/stores/form.html'
    # 🌟 モデルにある、運営者が入力すべきフィールドを網羅します
    fields = [
        'name', 'image', 'description', 'lower_price', 'upper_price', 
        'open_hours', 'zip_code', 'address', 'phone_number', 'holiday', 
        'is_published', 'category', 'tags'
    ]
    success_url = reverse_lazy('admin_store_list')

    def is_staff_user(self):
        return self.request.user.is_staff

    def test_func(self):
        return self.is_staff_user()


class AdminStoreUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Store
    template_name = 'admin_pages/stores/form.html'
    # 🌟 新規登録と同じフィールドを指定します
    fields = [
        'name', 'image', 'description', 'lower_price', 'upper_price', 
        'open_hours', 'zip_code', 'address', 'phone_number', 'holiday', 
        'is_published', 'category', 'tags'
    ]
    success_url = reverse_lazy('admin_store_list')

    def is_staff_user(self):
        return self.request.user.is_staff

    def test_func(self):
        return self.is_staff_user()


class AdminStoreDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Store
    template_name = 'admin_pages/stores/confirm_delete.html'
    success_url = reverse_lazy('admin_store_list')

    def is_staff_user(self):
        return self.request.user.is_staff

    def test_func(self):
        return self.is_staff_user()