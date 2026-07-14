from datetime import datetime, timedelta
import json
import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

# PremiumMember と Member のインポート
from base.models import Member, PremiumMember

stripe.api_key = settings.STRIPE_SECRET_KEY


# 1. チェックアウトセッション作成ビュー
class CreateCheckoutSessionView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        # 開発環境のドメイン（本番環境ではドメインを変更してください）
        domain_url = f"{request.scheme}://{request.get_host()}"

        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=request.user.email,  # ユーザーのメアドを自動入力
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": settings.STRIPE_PRICE_ID,
                        "quantity": 1,
                    },
                ],
                mode="subscription",  # サブスクリプションモードを指定
                # 成功URLに {CHECKOUT_SESSION_ID} パラメータを付与するように修正
                success_url=domain_url
                + reverse("premium_success")
                + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + reverse("premium_cancel"),
            )
            return redirect(checkout_session.url)
        except Exception as e:
            print(
                "❌ Stripeエラーが発生しました:", e
            )  # ターミナルにエラー内容を表示させる
            return redirect("home")


# 2. 決済成功時のビュー（StripeのサブスクIDを保存する処理を追加）
class PremiumSuccessView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        member = request.user.member

        # 現在の時刻を基準にする（サブスクリプションなので30日、あるいは1ヶ月追加）
        now = timezone.now()
        expiration_date = now + timedelta(days=30)  # ひとまず30日間有効として計算

        # URLのパラメータから Stripe の session_id を取得
        session_id = request.GET.get("session_id")
        stripe_subscription_id = None

        if session_id:
            try:
                # Stripeからセッションの詳細を引いて、サブスクリプションID（sub_xxx）を取得
                session = stripe.checkout.Session.retrieve(session_id)
                stripe_subscription_id = session.get("subscription")
            except Exception as e:
                print(f"❌ Stripeセッション取得エラー: {e}")

        # すでにPremiumMemberデータがあれば更新、なければ新規作成する（get_or_create）
        premium_member, created = PremiumMember.objects.get_or_create(
            member=member,
            defaults={
                "premium_expiration_date": expiration_date,
                "stripe_subscription_id": stripe_subscription_id,  # 新規作成時にIDを保存
            },
        )

        # もしすでに有料会員だった場合は、現在の有効期限、あるいは現在時刻からさらに30日延長する
        if not created:
            if premium_member.premium_expiration_date > now:
                # まだ期限が残っているなら、その期限から30日延長
                premium_member.premium_expiration_date += timedelta(days=30)
            else:
                # 期限が切れているなら、今から30日間に設定
                premium_member.premium_expiration_date = expiration_date

            # すでにデータが存在していた場合も、サブスクIDを最新の状態に上書き保存
            if stripe_subscription_id:
                premium_member.stripe_subscription_id = stripe_subscription_id

            premium_member.save()

        # # 運営管理画面側も連動させるため、Memberモデル自体の有料フラグも True に更新して保存
        # member.is_premium = True
        # member.save()

        return render(request, "pages/premium_success.html")


# 3. 決済キャンセル時のビュー
class PremiumCancelView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, "pages/premium_cancel.html")


# 4. Stripe Webhookの受け取りビュー（Webhook経由でもサブスクIDを確実に保存・更新）
@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = (
            settings.STRIPE_WEBHOOK_SECRET
        )
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except Exception as e:
            # 署名の検証に失敗した場合など
            return HttpResponse(status=400)

        # Stripeで決済（自動引き落とし含む）が成功した瞬間にこれが走ります！
        if event["type"] == "invoice.payment_succeeded":
            session = event["data"]["object"]
            customer_email = session.get("customer_email")

            # サブスクリプションの終了日（次の決済日 = 有効期限）を取得
            subscription_id = session.get("subscription")
            if subscription_id:
                subscription = stripe.Subscription.retrieve(subscription_id)
                # Stripeのタイムスタンプ（秒）をDjangoの日付型に変換
                expiration_date = datetime.fromtimestamp(
                    subscription["current_period_end"], tz=timezone.utc
                )

                # メールアドレスから会員を特定して期限を自動更新！
                try:
                    member = Member.objects.get(user__email=customer_email)
                    premium_member, created = (
                        PremiumMember.objects.get_or_create(
                            member=member,
                            defaults={
                                "premium_expiration_date": expiration_date,
                                "stripe_subscription_id": subscription_id,  # Webhook時もIDを保存
                            },
                        )
                    )
                    if not created:
                        premium_member.premium_expiration_date = expiration_date
                        premium_member.stripe_subscription_id = (
                            subscription_id  # 既存データ時もIDを更新
                        )
                        premium_member.save()

                    # 会員フラグも確実に有料状態にする
                    member.is_premium = True
                    member.save()

                    print(
                        f"✅ {customer_email} の有料会員期限を {expiration_date} に更新しました。"
                    )
                except Member.DoesNotExist:
                    pass

        return HttpResponse(status=200)


# 5. 有料会員の解約ビュー（Stripe自動更新停止と管理画面フラグの書き換えを完全同期）
class WithdrawPremiumView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        member = request.user.member

        # 1. Stripe側のサブスクリプションを停止する処理
        # 追加した 'stripe_subscription_id' フィールドを参照して決済停止命令を送る
        if (
            hasattr(member, "premium_member")
            and member.premium_member.stripe_subscription_id
        ):
            try:
                # Stripe APIを叩いてサブスクを期末解約（自動更新停止）にする
                stripe.Subscription.modify(
                    member.premium_member.stripe_subscription_id,
                    cancel_at_period_end=True,  # 期末（次の決済日）に自動解約する場合
                )
            except stripe.error.StripeError as e:
                # Stripe側でエラーが起きた場合は処理を中断してエラーメッセージを表示
                messages.error(request, f"Stripeでの解約処理に失敗しました: {e}")
                return redirect("/profile")

        # 2. Djangoデータベース側の有料会員データを削除・変更
        if hasattr(member, "premium_member"):
            member.premium_member.delete()

        # 運営側画面（管理画面フラグ）も確実に無料会員（False）に書き換えて保存
        # member.is_premium = False
        # member.save()

        messages.success(request, "プレミアム会員の解約手続きが完了しました。")
        return redirect("/profile")