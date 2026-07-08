from django.db import models
from base.models import Store  # 店舗モデルをインポート
# ※Memberモデルが別ファイルにある場合は適宜インポートしてください

class Favorite(models.Model):
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(
        "Member", on_delete=models.CASCADE, related_name="favorites"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="favorited_by"
    )
    # 🌟 いつお気に入りしたかを記録できる（一覧を新しい順に並べる時に便利）
    created_at = models.DateTimeField(auto_now_add=True)

    # 同じユーザーが同じ店舗を二重にお気に入り登録できないようにする設定
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'store'], 
                name='unique_member_store_favorite'
            )
        ]

    def __str__(self):
        return f"{self.member.user.username} - {self.store.name}"