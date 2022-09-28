from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
from blog.models import Comment, Post


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(default='default.jpg', upload_to='profile_pics')
	bio = models.TextField(default='bottom texte a', max_length=240)
	# change User to 'self'
	# doesn't make sense that profiles follow users
	followers = models.ManyToManyField(User, related_name='following', blank=True)

	def __str__(self):
		return f'{self.user.username} Profile'

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		img = Image.open(self.image.path)
		img = img.resize((300, 300), Image.ANTIALIAS)
		img.save(self.image.path)

class Notification(models.Model):
	# 1 = Like, 2 = Follow, 3 = Comment on your post, 4 = Responded to your comment
	notif_type = models.IntegerField(default=2)

	to_user = models.ForeignKey(User, related_name='notification_to', on_delete=models.CASCADE, null=True)
	from_user = models.ForeignKey(User, related_name='notification_from', on_delete=models.CASCADE, null=True)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
	message = models.TextField()
	date = models.DateTimeField(default=timezone.now)
	user_has_seen = models.BooleanField(default=False)