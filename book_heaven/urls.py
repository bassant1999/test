from django.urls import path
from . import views
# app_name = "book_heaven"
urlpatterns = [
   # start page
   path("",views.start,name="start"),
   path("about_us",views.about_us,name="about_us"),
   # home page
   path("home",views.home,name="home"), 
   path("home/my_library",views.my_library_view,name="my_library"), 
   path("home/remove_library",views.remove_lib,name ="remove_lib"),
   # home_paid_books
   path("home/paid_books",views.home_paid_books,name="home_paid_books"), 
   # login page             
   path("login", views.login_view, name="login"),
   path("logout", views.logout_view, name="logout"),
   # signup page
   path("signup", views.signup_view_1, name="signup_1"),
   path("signup_continue", views.signup_view_2, name="signup_2"),
   path("signup_helper", views.signup_helper, name="signup_helper"),
   # account page
   path("myAccount",views.myAccount_view,name="my_account"),
   path("myAccount/upload",views.upload_library,name="upload_library"),
   # free book page
   path("free_book/<int:free_book_id>",views.free_book,name="free_book"), 
   path("free_book/<int:free_book_id>/read",views.free_book_read,name="free_book_read"), 
   path("fbook_to_library/<int:free_book_id>", views.fbook_to_library, name="fbook_to_library"),
   path("free_book/frating_stars",views.frating_stars,name="frating_stars") ,
   # review free book 
   path("free_book/review_free_book",views.review_free_book,name="review_free_book"), 
   # Paid book page
   path("paid_book/<int:paid_book_id>",views.paid_book,name="paid_book"), 
   path("book_to_library/<int:paid_book_id>", views.book_to_library, name="book_to_library"),
   path("paid_book/rating_stars",views.rating_stars,name="rating_stars") ,
   # review paid book 
   path("paid_book/review_paid_book",views.review_paid_book,name="review_paid_book"),
   # search page
   path("home/search", views.search_view, name="search"),
   # path("home/search/fhelper", views.fsearch_helper, name="fsearch_helper"),
   # path("home/search/phelper", views.psearch_helper, name="psearch_helper")
   ]

# new
# upload files
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
