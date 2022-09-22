from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, CommentCreateView, UserPostListView, LikeView, FollowUserView, delete_comment, create_comment
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('about/', views.about, name='blog-about'),
    path('hall-of-shame', views.hall_of_shame, name='hall-of-shame'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('comment-delete/', delete_comment, name='comment-delete'),
	path('create-comment/', create_comment, name='comment-create'),
    path('follow-user/', FollowUserView, name='follow-user'),
    path('like/', LikeView, name='like-post'),
]
