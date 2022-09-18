from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Post(models.Model):
	title = models.CharField(max_length=100)
	content = models.TextField(max_length=1200, blank=True)
	date_posted = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
	dislikes = models.ManyToManyField(User, related_name='disliked_posts', blank=True)
	image = models.ImageField(upload_to='post_images', blank=True)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('post-detail', kwargs={'pk': self.pk})

	def total_likes(self):
		return self.likes.count() - self.dislikes.count()

	def has_liked(self, user_id):
		return self.likes.filter(id=user_id).exists()

class Comment(models.Model):
	post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
	content = models.TextField()
	date_posted = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	# every comment has one parent, but can have many replies
	parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

	class Meta:
    	# sort comments in chronological order by default
		ordering = ('date_posted',)

	# This is just what comes up under admin.
	def __str__(self):
		return 'Comment by {}'.format(self.author)

	def get_absolute_url(self):
		return reverse('post-detail', kwargs={'pk': self.pk})