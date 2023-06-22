from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(paid_books)
admin.site.register(paid_books_genres)
admin.site.register(paid_books_library)
admin.site.register(paid_books_rating)
admin.site.register(paid_books_review)
admin.site.register(free_books)
admin.site.register(free_books_genres)
admin.site.register(free_books_library)
admin.site.register(free_books_rating)
admin.site.register(free_books_review)