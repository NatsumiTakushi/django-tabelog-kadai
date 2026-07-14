from django.views.generic import UpdateView
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from base.models import Member, Reservation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib import messages
from django.views import View

class ProfileUpdateView(UpdateView):
    model = Member
    template_name = "pages/profile.html"
    # Memberモデルのフィールドを指定
    fields = ("zip_code", "address", "phone_number")
    success_url = "/profile/"

    def get_object(self, queryset=None):
        # ログイン中なら自分のMemberを返す。未ログインなら空の仮インスタンスを渡してエラーを防ぐ
        if self.request.user.is_authenticated:
            member, created = Member.objects.get_or_create(user=self.request.user)
            return member
        return Member()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # テンプレート側で「ログイン中かどうか」を正確に判定してデザインを切り替えるために渡す
        context['is_authenticated'] = self.request.user.is_authenticated
        if self.request.user.is_authenticated:
            context['reservations'] = Reservation.objects.filter(
                member=self.request.user.member
            ).order_by('-reservation_date', '-reservation_time')
        return context

    def form_valid(self, form):
        # ───────────────
        # Aパターン：未ログイン（新規会員登録）の処理
        # ───────────────
        if not self.request.user.is_authenticated:
            # 1. 画面から送られてきたUser用のデータを手動で回収
            username = self.request.POST.get('username')
            email = self.request.POST.get('email')
            password = self.request.POST.get('password')
            
            # 2. まず User（アカウント）を作成
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # 3. 画面の入力内容（zip_codeなど）を持ったMemberに、今作ったUserを紐付ける
            member = form.save(commit=False)
            member.user = user
            member.save()
            
            # 4. そのまま自動ログインさせてトップページへ
            login(self.request, user)
            return redirect('home')

        # ───────────────
        # Bパターン：ログイン済（通常のプロフィール更新）の処理
        # ───────────────
        else:
            # 1. ログイン中の User 情報（Username, Email）も一緒に更新する
            user = self.request.user
            user.username = self.request.POST.get('username', user.username)
            user.email = self.request.POST.get('email', user.email)
            user.save()
            
            # 2. Member情報の保存（UpdateView本来の動き）
            return super().form_valid(form)

# 一般会員の退会（アカウント完全削除）
class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        
        # アカウント削除（紐づくMemberデータも CASCADE で自動削除されます）
        user.delete()
        
        # セッションをクリアしてログアウト状態にする
        logout(request)
        
        messages.success(request, "退会手続きが完了しました。ご利用ありがとうございました。")
        return redirect('home')