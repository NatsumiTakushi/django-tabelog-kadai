from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.contrib import messages  # 🌟 メッセージ機能をインポート
from django.contrib.auth import logout  # 🌟 ログアウト機能をインポート
from django.utils import timezone  # 🌟 タイムゾーンをインポート
from dateutil.relativedelta import relativedelta  # 🌟 月単位の日付計算
import json  # 🌟 JSON変換用
from base.models import PremiumMember  # 🌟 有料会員モデルをインポート

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    
    # スタッフ（運営側）かどうかの判定条件
    def is_staff_user(self):
        return self.request.user.is_staff

    # UserPassesTestMixin用の権限検証メソッド
    def test_func(self):
        return self.is_staff_user()

    # 判定に失敗した場合の挙動
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # 🌟 ログインはしてるけどスタッフじゃない場合
            # 1. 画面に表示する警告メッセージを登録
            messages.error(self.request, "❌ 管理者権限がありません。運営者アカウントでログインしてください。")
            # 2. 一般セッションを一度クリア（ログアウト）する
            logout(self.request)
            # 3. メッセージを持たせたままログイン画面へ強制送還
            return redirect('login')
        else:
            # そもそもログインしていない場合は、次に戻るURLを仕込んでログイン画面へ
            login_url = reverse('login')
            next_url = self.request.get_full_path()
            return redirect(f"{login_url}?next={next_url}")

    def get(self, request, *args, **kwargs):
        # 現在有効な有料会員数をカウント
        now = timezone.now()
        total_premium_members = PremiumMember.objects.filter(premium_expiration_date__gt=now).count()
        # 今月の売上（月額300円 × 有料会員数）を計算
        sales_this_month = total_premium_members * 300

        # 🌟 過去12ヶ月の月別売上データを集計
        chart_labels = []
        chart_members = []
        chart_sales = []

        for i in range(11, -1, -1):
            # i ヶ月前の月初・月末を計算
            target_month = (now - relativedelta(months=i)).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            next_month = target_month + relativedelta(months=1)

            # その月に登録された有料会員数
            count = PremiumMember.objects.filter(
                created_at__gte=target_month,
                created_at__lt=next_month,
            ).count()

            # macOSでは %-m が使えないため %m + lstrip('0') で代替
            month_label = target_month.strftime('%Y年') + target_month.strftime('%m').lstrip('0') + '月'
            chart_labels.append(month_label)
            chart_members.append(count)
            chart_sales.append(count * 300)

        context = {
            'total_premium_members': total_premium_members,
            'sales_this_month': sales_this_month,
            # グラフ用データ（JSに渡すためjson.dumpsで文字列化）
            'chart_labels_json': json.dumps(chart_labels, ensure_ascii=False),
            'chart_members_json': json.dumps(chart_members),
            'chart_sales_json': json.dumps(chart_sales),
        }
        return render(request, 'admin_pages/dashboard/report.html', context)