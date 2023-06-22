from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    Birthday = models.DateField(null=True, blank=True)
# class User(AbstractUser):
#     user_mail = models.CharField(max_length=300, blank=True, unique=True, default = "@") 
#     Birthday = models.DateField(null=True, blank=True)

class paid_books(models.Model):
	Goodread_id = models.IntegerField()
	title = models.CharField(max_length=300, blank=True, null=True)
	original_title = models.CharField(max_length=300, blank=True, null=True)
	Authors = models.CharField(max_length=300, blank=True, null=True)
	link = models.CharField(max_length=400)
	Publication_year = models.IntegerField(blank=True, null=True)
	Average_rating = models.FloatField()
	Rating_count = models.IntegerField()
	Image_url = models.CharField(max_length=300, blank=True, null=True)
	small_image_url = models.CharField(max_length=300, blank=True, null=True)
	def serialize(self):
		return {
			"id": self.id,
			"Goodread_id": self.Goodread_id,
			"title": self.title,
			"Authors": self.Authors,
			"Image_url": self.Image_url,
			"Average_rating":self.Average_rating
		}


class paid_books_genres(models.Model):
	Book_id = models.ForeignKey(paid_books, on_delete=models.CASCADE, related_name="book_id")
	genre = models.CharField(max_length=200, blank=True, null=True)

class paid_books_library(models.Model):
	User_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_id")
	Book_id = models.ForeignKey(paid_books, on_delete=models.CASCADE, related_name="paid_book_id")

class paid_books_rating(models.Model):
	User_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_id_rate")
	Book_id = models.ForeignKey(paid_books, on_delete=models.CASCADE, related_name="paid_book_id_rate")
	rating = models.IntegerField()	

class paid_books_review(models.Model):
	User_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_id_review")
	Book_id = models.ForeignKey(paid_books, on_delete=models.CASCADE, related_name="paid_book_id_review")
	review = models.CharField(max_length=300, blank=True, null=True)
	Time_of_review = models.DateTimeField(auto_now_add=True)


class free_books(models.Model):
	Gutenberg_id = models.IntegerField()
	title = models.CharField(max_length=300, blank=True, null=True)
	Authors = models.CharField(max_length=300, blank=True, null=True)
	authoryearofbirth = models.IntegerField(blank=True, null=True)
	authoryearofdeath = models.IntegerField(blank=True, null=True)
	subjects = models.CharField(max_length=300, blank=True, null=True)
	Image_url = models.CharField(max_length=300, blank=True, null=True)
	Download_count = models.IntegerField()
	copy_right = models.CharField(max_length=300, blank=True, null=True)
	formats = models.CharField(max_length=400, blank=True, null=True)
	def serialize(self):
		return {
			"id": self.id,
			"Goodread_id": self.Gutenberg_id,
			"title": self.title,
			"Authors": self.Authors,
			"Image_url": self.Image_url,
			"Download_count":self.Download_count
		}

class free_books_genres(models.Model):
	Book_id = models.ForeignKey(free_books, on_delete=models.CASCADE, related_name="free_book_id")
	genre = models.CharField(max_length=200, blank=True, null=True)	


class free_books_library(models.Model):
	User_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_id_free")
	Book_id = models.ForeignKey(free_books, on_delete=models.CASCADE, related_name="free_book_id_lib")

class free_books_rating(models.Model):
	User_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_id_rate_free")
	Book_id = models.ForeignKey(free_books, on_delete=models.CASCADE, related_name="free_book_id_rate")
	rating = models.IntegerField()	

class free_books_review(models.Model):
	User_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_id_review_free")
	Book_id = models.ForeignKey(free_books, on_delete=models.CASCADE, related_name="free_book_id_review")
	review = models.CharField(max_length=300, blank=True, null=True)
	Time_of_review = models.DateTimeField(auto_now_add=True)

