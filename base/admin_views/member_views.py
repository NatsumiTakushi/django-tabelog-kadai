from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from base.models import Member

class AdminMemberListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Member
    template_name = 'admin_pages/members/list.html'
    context_object_name = 'members'
    paginate_by = 10

    def is_staff_user(self):
        return self.request.user.is_staff

    def test_func(self):
        return self.is_staff_user()

    def get_queryset(self):
        queryset = Member.objects.select_related('user', 'premium_member')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(user__username__icontains=query) |
                Q(user__email__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(address__icontains=query)
            )
        return queryset.order_by('-created_at')
