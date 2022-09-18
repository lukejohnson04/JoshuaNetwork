from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.views.generic import View
from .models import Notification

def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f'Your account has been created! You are now able to log in.')
			return redirect('login')
	else:
		form = UserRegisterForm()
	return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()

			messages.success(request, f'Account successfully updated!')
			return redirect('profile')

	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)

	context = {
		'u_form': u_form,
		'p_form': p_form
	}

	return render(request, 'users/profile.html', context)

class PostNotification(View):
	def get(self, request, notification_pk, post_pk, *args, **kwargs):
		notification = Notification.objects.get(pk=notification_pk)
		post = Post.objects.get(pk=post_pk)

		notification.user_has_seen = True
		notification.save()

		return redirect('post-detail', pk=post_pk)

class FollowNotification(View):
	def get(self, request, notification_pk, profile_pk, *args, **kwargs):
		notification = Notification.objects.get(pk=notification_pk)
		profile = Profile.objects.get(pk=post_pk)

		notification.user_has_seen = True
		notification.save()

		return redirect('post-detail', pk=profile_pk)

class RemoveNotificationView(View):
	def delete(self, request, notification_pk, *args, **kwargs):
		notification = Notification.objects.get(pk=notification_pk)

		notification.user_has_seen = True
		notification.save()

		HttpResponse('Success', content_type='text/plain')