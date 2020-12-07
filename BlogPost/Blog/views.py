from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from django.contrib.auth.models import User
from .models import Profile, Post, Comments
from .serializer import UserSerializer, UserPostSerializer, ProfileSerializer, UserUpdateSerializer, PostSerializer, CommentsSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from .permissions import IsAuthorOrIsAdminOrReadOnly



from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
# from rest_condition import Or
from rest_framework import permissions
# Create your views here.

class ListCreateUserView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = (DjangoFilterBackend,OrderingFilter, SearchFilter)
    filterset_fields = ('last_name', 'email')
    ordering_fields = ('last_name', 'first_name')
    search_fields = ('first_name', 'last_name', 'email', 'username')
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

class ListProfileView(ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUser]

class RetriveUpdateDeleteUser(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    # def get(self, *args, **kwargs):
    #     print('inside get method')
    #     return super().get(*args, **kwargs)

    # def put(self, *args, **kwargs):
    #     return super().put(*args, **kwargs)

    # def patch(self, request, *args, **kwargs):
    #     # self.request.data.pop('password')
    #     print('inside put method...........', self.request.data)
    #     # return super().patch(*args, **kwargs)
    #     return self.patch(request, *args, **kwargs)
    
class ListCreatePostView(ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,OrderingFilter, SearchFilter)
    filterset_fields = ('title','content','subtitle', 'published_at','author')
    ordering_fields = ('title','content','subtitle', 'published_at','author')
    search_fields = ('title','content','subtitle')
    
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
    def perform_create(self, serializer):
        print("author................", self.request.user)
        serializer.save(author=self.request.user)
    
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)

class RetrieveUpdateDestroyPost(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrIsAdminOrReadOnly]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class ListCreateCommentsView(ListCreateAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,OrderingFilter, SearchFilter)
    filterset_fields = ('content', 'created_at', 'active','author')
    ordering_fields = ('content', 'created_at', 'active','author')
    search_fields = ('content',)
    
    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        post= get_object_or_404(Post, pk=post_id)
        return Comments.objects.filter(post=post)
    
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        post= get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post=post)
    
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)

class RetrieveUpdateDestroyComments(RetrieveUpdateDestroyAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthorOrIsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,OrderingFilter, SearchFilter)
    search_fields = ('content',)
    filterset_fields = ('author',)
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

from drf_multiple_model.views import ObjectMultipleModelAPIView

from django.db.models import Q 
def FilterUsers(queryset, request, *args, **kwargs):
        search = request.query_params['search']        
        if request.user.is_superuser:
            result = queryset.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(username__icontains=search)) 
            return result
        return None

def FilterPosts(queryset, request, *args, **kwargs):
        search = request.query_params['search']        
        if not request.user.is_superuser:        
            queryset = queryset.filter(author= request.user)
        result = queryset.filter(Q(title__icontains=search) | Q(content__icontains=search) | Q(subtitle__icontains=search)) 
        return result

def FilterComments(queryset, request, *args, **kwargs):
        search = request.query_params['search']        
        if not request.user.is_superuser:        
            queryset = queryset.filter(author= request.user)
        result = queryset.filter(content__icontains=search)
        return result
        


class ListUsers(ObjectMultipleModelAPIView):
    querylist = [
        {'queryset': User.objects.all(), 'serializer_class': UserSerializer, 'filter_fn' : FilterUsers},
        {'queryset': Post.objects.all(), 'serializer_class': PostSerializer, 'filter_fn' : FilterPosts},
        {'queryset': Comments.objects.all(), 'serializer_class': CommentsSerializer, 'filter_fn' : FilterComments}
    ]
    
    queryset = User.objects.all()
    serializer_class = UserPostSerializer    
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = (DjangoFilterBackend,OrderingFilter, SearchFilter)
    # search_fields = ('first_name', 'last_name', 'title', 'content', 'subtitle')
    

    # def get_queryset(self):        
    #     return super().get_queryset()

    # def get(self, request, *args, **kwargs):
    #     return self.list(request, *args, **kwargs)

