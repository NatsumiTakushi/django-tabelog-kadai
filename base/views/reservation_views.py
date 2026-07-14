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
        
        if date_str:
            reservation.reservation_date = parse_date(date_str)
        if time_str:
            reservation.reservation_time = parse_time(time_str)
        if people_str:
            reservation.count = int(people_str)
            
        if self.request.user.is_authenticated:
            reservation.member = self.request.user.member
            
        pk = self.kwargs.get('pk')
        store = get_object_or_404(Store, pk=pk)
        reservation.store = store

        # ==========================================================
        # 🚨 【修正版】営業時間・定休日のバリデーションチェック
        # ==========================================================
        
        # ① 過去の日付チェック
        if reservation.reservation_date and reservation.reservation_date < localdate():
            messages.error(self.request, "過去の日付は予約できません。")
            return self.form_invalid_custom(form, store, date_str, time_str, people_str)

        # ② 定休日チェック（タイムゾーンのズレを防ぐ確実な方法）
        if reservation.reservation_date and store.holiday:
            # 予約日の曜日を「月曜日」「火曜日」といった文字列に変換
            # %A はロケール（環境）に応じて曜日名（日本語なら◯曜日）を返します
            import locale
            try:
                locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
            except Exception:
                pass # 本番環境のOSによって設定できない場合はスキップ
                
            # 確実な曜日マッピング（0=月, 1=火 ... 6=日）
            weekdays = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
            res_weekday_name = weekdays[reservation.reservation_date.weekday()]
            
            # 店舗の定休日（例: "火曜日"）と、選択された日（例: "火曜日"）を直接比較
            if store.holiday.strip() == res_weekday_name:
                messages.error(self.request, f"申し訳ありません。選択された日は{store.holiday}（定休日）です。")
                return self.form_invalid_custom(form, store, date_str, time_str, people_str)

        # ③ 営業時間チェック (どんな区切り文字でも対応できるように改良)
        if reservation.reservation_time and store.open_hours:
            try:
                # 区切り文字（~ や - や 〜）をすべて「~」に統一する
                normalized_hours = store.open_hours.replace('-', '~').replace('〜', '~').replace(' ', '')
                
                if '~' in normalized_hours:
                    # 文字列を「開始」と「終了」に分解
                    start_str, end_str = normalized_hours.split('~')
                    
                    # 💡 もし "11:00:00" のように秒まで含まれている場合にも対応
                    start_time = datetime.strptime(start_str.strip()[:5], '%H:%M').time()
                    end_time = datetime.strptime(end_str.strip()[:5], '%H:%M').time()
                    
                    # 予約時間が営業時間内に収まっているか判定
                    if not (start_time <= reservation.reservation_time <= end_time):
                        messages.error(self.request, f"予約時間は営業時間内（{store.open_hours}）で指定してください。")
                        return self.form_invalid_custom(form, store, date_str, time_str, people_str)
            except Exception as e:
                # 万が一エラーが起きても強制スルーせず、ログに出力して確認できるようにする
                print(f"❌ 営業時間パースエラー: {e}")

        # ==========================================================

        # すべてのチェックを通過した場合のみ、以下が実行されて保存されます
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