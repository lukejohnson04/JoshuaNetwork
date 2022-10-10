from django.urls import path
from .views import HomeListView, TrendingListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, CommentCreateView, UserPostListView, LikeView, FollowUserView, delete_comment, create_comment, LikeCommentView
from . import views

urlpatterns = [
    path('', HomeListView.as_view(), name='blog-home'),
    path('trending', TrendingListView.as_view(), name='trending'),
    path('about/', views.about, name='blog-about'),
    path('hall-of-shame', views.hall_of_shame, name='hall-of-shame'),
    path('@<str:username>/', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('comment-delete/', delete_comment, name='comment-delete'),
	path('create-comment/', create_comment, name='comment-create'),
    path('follow-user/', FollowUserView, name='follow-user'),
    path('like-post/', LikeView, name='like-post'),
    path('like-comment/', LikeCommentView, name='like-comment'),    
]
