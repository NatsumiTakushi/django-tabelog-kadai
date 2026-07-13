from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

# Django標準のUserモデル（username, email, password を最初から持っています）
User = get_user_model()


def create_id():
    return get_random_string(22)


# Userとは別に、会員情報を管理するモデルを作成
class Member(models.Model):
    id = models.CharField(
        default=create_id, primary_key=True, max_length=22, editable=False
    )

    # 標準のUserと1対1で紐付け
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="member")

    # 独自の追加フィールド
    zip_code = models.CharField(default="", max_length=50)
    address = models.CharField(default="", max_length=100)
    phone_number = models.CharField(default="", max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} の会員情報"

    # 有効期限を見て自動で判定するプロパティ（データベースには保存されません）
    @property
    def is_premium(self):
        try:
            return self.premium_member.premium_expiration_date > timezone.now()
        except AttributeError:
            return False


# プレミアムユーザーもMemberに紐付ける形
class PremiumMember(models.Model):
    id = models.CharField(
        default=create_id, primary_key=True, max_length=22, editable=False
    )
    member = models.OneToOneField(
        Member, on_delete=models.CASCADE, related_name="premium_member"
    )
    premium_expiration_date = models.DateTimeField()

    # StripeのサブスクIDを保存するフィールドをここに追加！
    stripe_subscription_id = models.CharField(
        max_length=255, blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)