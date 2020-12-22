from django.urls import path, include
from .views import (ListCreateUserView, ListProfileView, RetriveUpdateDeleteUser, ListUsers,
ListCreatePostView, RetrieveUpdateDestroyPost, 
ListCreateCommentsView, RetrieveUpdateDestroyComments, ApiSearch)

urlpatterns = [
    path('users/', ListCreateUserView.as_view(), name = "userslist"),
    path('users/<int:pk>', RetriveUpdateDeleteUser.as_view(), name = "detailuser"),
    path('users-posts/', ListUsers.as_view(), name = "detailuser"),    
    path('profiles/', ListProfileView.as_view(), name = "profilelist"),
    path('posts/', ListCreatePostView.as_view(), name= "postlist"),
    path('posts/<int:pk>', RetrieveUpdateDestroyPost.as_view(), name= "detailpost"),    
    path('posts/<int:post_id>/comments/', ListCreateCommentsView.as_view(), name= "commentslist"),
    path('posts/<int:post_id>/comments/<int:pk>', RetrieveUpdateDestroyComments.as_view(), name= "detailcommnets"),  
    path('searchdb/', ApiSearch.as_view(), name = "search")  
]
