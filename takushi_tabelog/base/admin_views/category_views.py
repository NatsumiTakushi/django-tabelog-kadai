from django.shortcuts import redirect
from django.views.generic import ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django import forms
from base.models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['slug', 'name']
        labels = {
            'slug': 'カテゴリコード（Slug）',
            'name': 'カテゴリ名',
        }
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: italian'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: イタリアン'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug.isalnum() and not all(c in '-_' for c in slug if not c.isalnum()):
            raise forms.ValidationError("カテゴリコードは半角英数字、ハイフン、アンダースコアのみ使用できます。")
        return slug

class AdminCategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = 'admin_pages/categories/list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def is_staff_user(self):
        return self.request.user.is_staff

    def test_func(self):
        return self.is_staff_user()

    def get_queryset(self):
        return Category.objects.all().order_by('slug')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = CategoryForm()
        return context

    def post(self, request, *args, **kwargs):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_category_list')
        
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))


class AdminCategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    template_name = 'admin_pages/categories/confirm_delete.html'
    success_url = reverse_lazy('admin_category_list')

    def is_staff_user(self):
        return self.request.user.is_staff

    def test_func(self):
        return self.is_staff_user()
