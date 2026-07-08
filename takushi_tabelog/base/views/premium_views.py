import stripe
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.views import View
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
# 🌟 PremiumMember も合わせてインポートします
from base.models import Member, PremiumMember 
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

# ... CreateCheckoutSessionView などは既存のままでOK ...
class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # 開発環境のドメイン（本番環境ではドメインを変更してください）
        domain_url = "http://127.0.0.1:8000"
        
        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=request.user.email, # ユーザーのメアドを自動入力
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': settings.STRIPE_PRICE_ID,
                        'quantity': 1,
                    },
                ],
                mode='subscription', # サブスクリプションモードを指定
                success_url=domain_url + reverse('premium_success'),
                cancel_url=domain_url + reverse('premium_cancel'),
            )
            return redirect(checkout_session.url)
        except Exception as e:
            print("❌ Stripeエラーが発生しました:", e) # 🌟 ターミナルにエラー内容を表示させる
            return redirect('home')
# 2. 決済成功時のビュー（PremiumMemberモデルに対応）
class PremiumSuccessView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        member = request.user.member
        
        # 現在の時刻を基準にする（サブスクリプションなので30日、あるいは1ヶ月追加）
        now = timezone.now()
        expiration_date = now + timedelta(days=30) # 💡ひとまず30日間有効として計算
        
        # 🌟 すでにPremiumMemberデータがあれば更新、なければ新規作成する（get_or_create）
        premium_member, created = PremiumMember.objects.get_or_create(
            member=member,
            defaults={'premium_expiration_date': expiration_date}
        )
        
        # もしすでに有料会員だった場合は、現在の有効期限、あるいは現在時刻からさらに30日延長する
        if not created:
            if premium_member.premium_expiration_date > now:
                # まだ期限が残っているなら、その期限から30日延長
                premium_member.premium_expiration_date += timedelta(days=30)
            else:
                # 期限が切れているなら、今から30日間に設定
                premium_member.premium_expiration_date = expiration_date
            premium_member.save()

        return render(request, 'pages/premium_success.html')

class PremiumCancelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'pages/premium_cancel.html')