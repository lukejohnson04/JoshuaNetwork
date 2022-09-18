from django import template
from users.models import Notification, Profile

register = template.Library()

@register.inclusion_tag('render_post.html')
def render_post_func(post, user):
	karma = 0
	if post.likes.filter(id=user.id).exists():
		karma = 1
	elif post.dislikes.filter(id=user.id).exists():
		karma = -1
	return {'post': post, 'user': user, 'karma': karma}

@register.inclusion_tag('render_user_sidebar.html')
def render_user_sidebar(user_to_render, user):
	is_following = False
	if user_to_render.profile.followers.filter(pk=user.pk).exists():
		is_following = True
	return {'user_to_render': user_to_render, 'user': user, 'is_following': is_following}

@register.inclusion_tag('users/show_notifications.html', takes_context=True)
def show_notifications(context):
	request_user = context['request'].user
	notifications = Notification.objects.filter(to_user=request_user).exclude(user_has_seen=True).order_by('-date')
	return {'notifications': notifications}

@register.inclusion_tag('blog/render_comment.html')
def render_comment(comment, user):
	return {'comment': comment, 'user': user}