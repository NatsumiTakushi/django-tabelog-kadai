from django.views import View
from django.views.generic import CreateView
from django.shortcuts import redirect, get_object_or_404, render # ⭕️ render を追加
from django.urls import reverse_lazy
from django.contrib import messages # ⭕️ messages を追加
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.dateparse import parse_date, parse_time
from django.utils.timezone import localdate # ⭕️ localdate を追加
from datetime import datetime # ⭕️ datetime を追加
from base.models import Reservation, Store 

class ReservationCreateView(CreateView):
    model = Reservation
    fields = []
    success_url = reverse_lazy('home')
    template_name = 'pages/reservation_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_date'] = self.request.GET.get('date')
        context['selected_time'] = self.request.GET.get('time')
        context['selected_people'] = self.request.GET.get('people')
        
        pk = self.kwargs.get('pk')
        context['store'] = get_object_or_404(Store, pk=pk)
        return context

    def form_valid(self, form):
        reservation = form.save(commit=False)
        
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
        store = get_object_or_404(Store, pk=pk)
        reservation.store = store

        # ==========================================================
        # 🚨 【追加】営業時間・定休日のバリデーションチェック
        # ==========================================================
        
        # ① 過去の日付チェック
        if reservation.reservation_date and reservation.reservation_date < localdate():
            messages.error(self.request, "過去の日付は予約できません。")
            return self.form_invalid_custom(form, store, date_str, time_str, people_str)

        # ② 定休日チェック
        if reservation.reservation_date and store.holiday:
            weekday_map = {"月曜日": 0, "火曜日": 1, "水曜日": 2, "木曜日": 3, "金曜日": 4, "土曜日": 5, "日曜日": 6}
            if store.holiday in weekday_map:
                if reservation.reservation_date.weekday() == weekday_map[store.holiday]:
                    messages.error(self.request, f"申し訳ありません。選択された日は{store.holiday}（定休日）です。")
                    return self.form_invalid_custom(form, store, date_str, time_str, people_str)

        # ③ 営業時間チェック (open_hours が "11:00~21:00" のように「~」で区切られている前提)
        if reservation.reservation_time and store.open_hours and '~' in store.open_hours:
            try:
                start_str, end_str = store.open_hours.split('~')
                start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
                end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
                
                if not (start_time <= reservation.reservation_time <= end_time):
                    messages.error(self.request, f"予約時間は営業時間内（{store.open_hours}）で指定してください。")
                    return self.form_invalid_custom(form, store, date_str, time_str, people_str)
            except ValueError:
                pass # パースに失敗した場合は安全のためスルーします

        # ==========================================================

        # Djangoのバリデーションチェックを強制通過させる処理
        form.instance.reservation_date = reservation.reservation_date
        form.instance.reservation_time = reservation.reservation_time
        form.instance.count = reservation.count
        form.instance.store = reservation.store
        if hasattr(reservation, 'member'):
            form.instance.member = reservation.member

        messages.success(self.request, "予約が完了しました！")
        return super().form_valid(form)

    # ⭕️ エラー時に画面を正しく再表示するためのカスタムメソッド
    def form_invalid_custom(self, form, store, date, time, people):
        context = self.get_context_data()
        # エラーが起きた時も、ユーザーが入力していた値をそのまま引き継ぐ
        context['selected_date'] = date
        context['selected_time'] = time
        context['selected_people'] = people
        context['form'] = form
        return render(self.request, self.template_name, context)

class ReservationCancelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # 1. 対象の予約データを取得
        reservation = get_object_or_404(Reservation, pk=self.kwargs['pk'])
        
        # 2. セキュリティ対策：他のユーザーが勝手にキャンセルできないようにチェック
        if reservation.member != request.user.member:
            raise PermissionDenied("他人の予約をキャンセルすることはできません。")
            
        # 3. 予約データをデータベースから削除
        reservation.delete()
        
        # 4. 処理が終わったら、プロフィール画面（マイページ）にリダイレクト
        return redirect('account') # urls.pyでのプロフィール画面の名前（profileやaccountなど）に合わせてください