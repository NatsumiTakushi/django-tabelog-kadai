# base/views/reservation_views.py
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.dateparse import parse_date, parse_time
from base.models import Reservation, Store 

class ReservationCreateView(CreateView):
    model = Reservation
    fields = []
    success_url = reverse_lazy('home')
    template_name = 'base/reservation_form.html'
    
    # 💡 役割1：店舗詳細画面から遷移してきた時（GET）に画面に表示する処理
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_date'] = self.request.GET.get('date')
        context['selected_time'] = self.request.GET.get('time')
        context['selected_people'] = self.request.GET.get('people')
        
        pk = self.kwargs.get('pk')
        context['store'] = get_object_or_404(Store, pk=pk)
        return context

    # 💡 役割2：Djangoの自動チェック（バリデーション）の前に、データを強制的に仕込む処理
    def form_valid(self, form):
        reservation = form.save(commit=False)
        
        # ⭕️ 改善：POST（隠しフィールド）と GET（URLのパラメータ）の「両方」からデータを安全に探します
        date_str = self.request.POST.get('date') or self.request.GET.get('date')
        time_str = self.request.POST.get('time') or self.request.GET.get('time')
        people_str = self.request.POST.get('people') or self.request.GET.get('people')
        
        # モデルにデータをセット
        if date_str:
            reservation.reservation_date = parse_date(date_str)
        if time_str:
            reservation.reservation_time = parse_time(time_str)
        if people_str:
            reservation.count = int(people_str)
            
        # ユーザー情報の紐付け
        if self.request.user.is_authenticated:
            reservation.member = self.request.user.member
            
        # 店舗情報の紐付け
        pk = self.kwargs.get('pk')
        reservation.store = get_object_or_404(Store, pk=pk)

        # ⭕️ 最重要：Djangoのバリデーションチェックを強制通過させるため、formのinstanceにも直接値を格納します
        form.instance.reservation_date = reservation.reservation_date
        form.instance.reservation_time = reservation.reservation_time
        form.instance.count = reservation.count
        form.instance.store = reservation.store
        if hasattr(reservation, 'member'):
            form.instance.member = reservation.member

        return super().form_valid(form)