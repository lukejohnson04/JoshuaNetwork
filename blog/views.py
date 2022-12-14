from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Count, Q

from django.utils import timezone
from math import log

from .models import Post, Comment
from users.models import Profile, Notification
from .forms import CommentForm
from PIL import Image

def home(request):
	context = {
		'posts': Post.objects.filter(likes.count()),
		'user_count': 5#User.objects.count(),
	}
	sort_type = request.GET.get("sort-type"),
	return render(request, 'blog/home.html', context)

def hall_of_shame(request):
	shame_user = Profile.objects.order_by('followers').first().user
	# Make this the post with lowest difference between likes and dislikes
	posts = Post.objects.annotate(karma=Count('likes')-Count('dislikes'))
	shame_post = posts.order_by('karma').first()
	context = {
		'shame_user': shame_user,
		'shame_post': shame_post
	}
	return render(request, 'blog/hall_of_shame.html', context)

# add support for this to work on comments
def LikeView(request):
	is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
	if is_ajax and request.method == "GET":
		post_pk = request.GET.get("post")
		btn = int(request.GET.get("btn"))
		post = Post.objects.filter(pk=post_pk)

		if post.exists():
			post = post.first()
			present_in_likes = post.likes.filter(id=request.user.id).exists()
			present_in_dislikes = post.dislikes.filter(id=request.user.id).exists()
			karma = 0
			# pressed like button
			if btn == 1:
				if present_in_dislikes:
					post.dislikes.remove(request.user)
				if not present_in_likes:
					post.likes.add(request.user)
					karma = 1
				else:
					post.likes.remove(request.user)
					karma = 0
			# pressed dislike button
			elif btn == -1:
				if present_in_likes:
					post.likes.remove(request.user)
				if not present_in_dislikes:
					post.dislikes.add(request.user)
					karma = -1
				else:
					post.dislikes.remove(request.user)
			return JsonResponse({"valid": True, "karma": karma, "post_likes": post.total_likes()}, status=200)
		else:
			return JsonResponse({"valid": False, "karma": karma, "post_likes": post.total_likes()}, status=200)
	return JsonResponse({}, status=400)

def process_like_outcome(obj, user, btn):
	present_in_likes = obj.likes.filter(id=user).exists()
	present_in_dislikes = obj.dislikes.filter(id=user).exists()
	karma = 0
	# pressed like button
	if btn == 1:
		if present_in_dislikes:
			obj.dislikes.remove(user)
		if not present_in_likes:
			obj.likes.add(user)
			karma = 1
		else:
			obj.likes.remove(user)
			karma = 0
	# pressed dislike button
	elif btn == -1:
		if present_in_likes:
			obj.likes.remove(user)
		if not present_in_dislikes:
			obj.dislikes.add(user)
			karma = -1
		else:
			obj.dislikes.remove(user)
	return karma

def LikeCommentView(request):
	is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
	if is_ajax and request.method == "POST":
		comment_pk = request.POST.get("comment")
		btn = int(request.POST.get("btn"))
		comment = Comment.objects.filter(pk=comment_pk)

		if comment.exists():
			comment = comment.first()
			karma = process_like_outcome(comment, request.user.id, btn)
			return JsonResponse({"valid": True, "karma": karma, "comment_likes": comment.total_likes()}, status=200)
		else:
			return JsonResponse({"valid": False}, status=200)
	return JsonResponse({}, status=400)

def delete_comment(request):
	is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
	if is_ajax and request.method == "GET":
		comment_pk = request.GET.get("comment")
		comment = Comment.objects.filter(pk=comment_pk)
		if comment.exists():
			comment.delete()
			return JsonResponse({"valid": True, "deleted": True}, status=200)
		return JsonResponse({"valid": False, "deleted": False}, status=400)
	return JsonResponse({}, status=400)

def FollowUserView(request):
	# user is the user you're trying to follow
	# current user is simply request.user
	is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
	if is_ajax and request.method == "GET":
		user_pk = request.GET.get("user-pk")
		user = get_object_or_404(User, pk=user_pk)
		unfollowed = False
		if user.profile.followers.filter(id=request.user.id).exists():
			user.profile.followers.remove(request.user)
			# unfollow
			unfollowed = True
		else:
			user.profile.followers.add(request.user)
			# add code to remove old notif w obj
			notif = Notification.objects.create(notif_type=2, from_user=request.user, to_user=user)
			unfollowed = False
		# make return invalid instead of just using get_object_or_404
		return JsonResponse({"valid": True, "unfollowed": unfollowed, "follow-count": user.profile.followers.count()}, status=200)
	return JsonResponse({}, status=400)

class PostListView(ListView):
	model = Post
	context_object_name = 'posts'
	paginate_by = 5
	default_sort = 'hot'

	def get_queryset(self):
		sort_type = self.request.GET.get('sort_type', self.default_sort)
		return get_post_set(sort_type)

	def get_context_data(self, **kwargs):
		context = super(PostListView, self).get_context_data(**kwargs)
		context['sort_type'] = self.request.GET.get('sort_type', self.default_sort)
		context['user_count'] = User.objects.count()
		return context

class TrendingListView(PostListView):
	template_name = 'blog/home.html'

class HomeListView(PostListView):
	template_name = 'blog/home.html'
	default_sort = 'new'

	def get_queryset(self):
		logged_in = self.request.user.is_authenticated
		page_set = Post.objects

		if logged_in:
			page_set = page_set.filter(Q(author=self.request.user) | Q(author__profile__followers=self.request.user)).distinct()
		else:
			self.default_sort = 'hot'
	
		sort_type = self.request.GET.get('sort_type', self.default_sort)

		return get_post_set(sort_type, page_set)

class UserPostListView(PostListView):
	template_name = 'blog/user_posts.html'
	default_sort = 'new'

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		sort_type = self.request.GET.get('sort_type', self.default_sort)
		return get_post_set(sort_type, n_author=user)

	def get_context_data(self, **kwargs):
		context = super(UserPostListView, self).get_context_data(**kwargs)
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		context['sort_type'] = self.request.GET.get('sort_type', 'new')
		context['user_of_page'] = user
		
		return context

def get_post_set(ordering, post_set=Post.objects, n_author=None):
	base_set = post_set
	if n_author != None:
		base_set = base_set.filter(author=n_author)

	if ordering == "top":
		sort_type = "-karma"
	elif ordering == "controversial":
		sort_type = "karma"
	elif ordering == "new":
		sort_type = "-date_posted"
	elif ordering == "old":
		sort_type = "date_posted"
	elif ordering == "hot":
		# trending alg here
		post_dict = {}
		for post in base_set.all():
			# trending alg:
			# (likes*0.5 + unique commenters) * (1/days_ago^2)
			# just do number of comments for now, can do unique comments later
			days_since_posted = (timezone.now() - post.date_posted).days
			if days_since_posted <= 1:
				date_weight = 1
			else:
				date_weight = 1/days_since_posted**2
			sort_weight = ((post.likes.count() + 1 + post.comments.count()) / (post.dislikes.count()+1)) * date_weight
			post_dict[post.pk] = sort_weight
		post_dict = dict(sorted(post_dict.items(), reverse=True, key=lambda item: item[1]))
		post_list = []
		for post in post_dict.keys():
			post_list.append(Post.objects.get(pk=post))
		return post_list

	if sort_type == "karma" or sort_type == "-karma":
		base_set = base_set.annotate(karma=Count('likes')-Count('dislikes'))
	return base_set.order_by(sort_type)

def get_post_list(n_sort_type=None, n_author=None):
	sort_type = n_sort_type

	# default to sorting by new
	if sort_type == "new" or sort_type == None:
		sort_type = "-date_posted"
	elif sort_type == "top":
		sort_type = "-likes"
	elif sort_type == "hot":
		sort_type = "likes"

	if n_author == None:
		return Post.objects.order_by(sort_type)
	else:
		return Post.objects.filter(author=n_author).order_by(sort_type)

class PostDetailView(DetailView):
	model = Post
	context_object_name = 'post'

	def get_context_data(self, **kwargs):
		context = super(PostDetailView, self).get_context_data(**kwargs)
		post = get_object_or_404(Post, id=self.kwargs['pk'])
		context['total_likes'] = post.total_likes
		top_comments = post.comments.filter(parent=None) # filter by likes lol wtf is this
		context['top_comments'] = top_comments
		return context

class PostCreateView(LoginRequiredMixin, CreateView):
	model = Post
	fields = ['title', 'content', 'image']
	
	# Function run when button is pressed
	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	fields = ['title', 'content']

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			return True
		return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Post

	success_url = '/'

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			return True
		return False

def create_comment(request):
	is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
	if is_ajax and request.method == "POST":
		post_pk = request.POST.get("post")
		content = request.POST.get("content")
		post = Post.objects.filter(pk=post_pk)

		# pass content of comment argument
		if post.exists():
			post = post.first()
			parent_comment_pk = request.POST.get("parent")
			# Check if it's a head comment or not
			parent_comment = None
			if parent_comment_pk != "":
				parent_comment = Comment.objects.filter(pk=parent_comment_pk)
				if parent_comment.exists():
					parent_comment = parent_comment.first()
				else:
					parent_comment = None
			
			responding_to = None
			notif_author = True
			if post.author == request.user:
				notif_author = False

			# Check if the comment starts with pinging a user
			if content[0] == '@':
				ping_msg = content.split()[0]
				responding_to = User.objects.filter(username=ping_msg[1:len(ping_msg)])
				if responding_to.exists():
					responding_to = responding_to.first()
					# notify them that you responded to their comment
					if request.user != responding_to:
						notif = Notification.objects.create(notif_type=4, from_user=request.user, to_user=responding_to, post=post)
						notif_author = False
				else:
					responding_to = None
			# Don't notify someone twice if they're both the parent comment author and within the thread
			if notif_author:
				notif = Notification.objects.create(notif_type=3, from_user=request.user, to_user=post.author, post=post)

			comment = Comment.objects.create(post=post, content=content, author=request.user, parent=parent_comment, responding_to=responding_to)
			response = render_to_string('blog/render_comment.html', context={"comment": comment, "user": request.user, "parent": parent_comment})
			return JsonResponse({"valid": True, "commented": True, "rendered-comment": response}, status=200)
		return JsonResponse({"valid": False, "commented": False}, status=400)
	return JsonResponse({}, status=400)

class CommentCreateView(LoginRequiredMixin, CreateView):
	model = Comment
	form_class = CommentForm
	template_name = 'blog/comment.html'

	def form_valid(self, form):
		form.instance.post_id = self.kwargs['pk']
		form.instance.author = self.request.user
		post = Post.objects.get(pk=self.kwargs['pk'])
		notif = Notification.objects.create(notif_type=2, from_user=self.request.user, to_user=post.author, post=post)
		return super().form_valid(form)

	def get_success_url(self):
		pk = self.kwargs["pk"]
		return reverse("post-detail", kwargs={"pk": pk})

def about(request):
	return render(request, 'blog/about.html', {'title': 'About'})
