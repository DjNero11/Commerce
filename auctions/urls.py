from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing",views.new_listing, name="new_listing"),
    path("listing/<int:listing_id>",views.listing_page_views, name="listing_page"),
    path("watchlist", views.watchlist_views, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category_page_views, name="category_page")
]
