from django.shortcuts import redirect
from django.views.generic import ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django import forms
from base.models import Tag

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['slug', 'name']
        labels = {
            'slug': 'タグコード（Slug）',
            'name': 'タグ名',
        }
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: ramen'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: ラーメン'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug.isalnum() and not all(c in '-_' for c in slug if not c.isalnum()):
            raise forms.ValidationError("タグコードは半角英数字、ハイフン、アンダースコアのみ使用できます。")
        return slug

class AdminTagListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Tag
    template_name = 'admin_pages/tags/list.html'
    context_object_name = 'tags'
    paginate_by = 20

    def is_staff_user(self):
        return self.request.user.is_staff

    def test_func(self):
        return self.is_staff_user()

    def get_queryset(self):
        return Tag.objects.all().order_by('slug')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = TagForm()
        return context

    def post(self, request, *args, **kwargs):
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_tag_list')
        
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))


class AdminTagDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tag
    template_name = 'admin_pages/tags/confirm_delete.html'
    success_url = reverse_lazy('admin_tag_list')

    def is_staff_user(self):
        return self.request.user.is_staff

    def test_func(self):
        return self.is_staff_user()
