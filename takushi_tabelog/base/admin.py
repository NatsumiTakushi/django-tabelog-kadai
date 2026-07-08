from django.contrib import admin
from base.models import Member, PremiumMember, Review, Reservation, Store, Category, Tag, Favorite
from django.contrib.auth.admin import UserAdmin
# Register your models here.
admin.site.register(Member)
admin.site.register(PremiumMember)
admin.site.register(Review)
admin.site.register(Reservation)
admin.site.register(Store)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Favorite)