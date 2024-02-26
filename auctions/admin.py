from django.contrib import admin

from .models import User, listing, bid, comment, category, watchlist
# Register your models here.

class watchlistAdmin(admin.ModelAdmin):
    filter_horizontal = ("items",)


admin.site.register(User)
admin.site.register(listing)
admin.site.register(bid)
admin.site.register(comment)
admin.site.register(category)
admin.site.register(watchlist,watchlistAdmin)
