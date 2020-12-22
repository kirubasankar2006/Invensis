from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from django.contrib.auth.models import User
from .models import Profile, Post, Comments
from .serializer import UserSerializer, UserPostSerializer, ProfileSerializer, UserUpdateSerializer, PostSerializer, CommentsSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from .permissions import IsAuthorOrIsAdminOrReadOnly
from rest_framework.parsers import MultiPartParser, FileUploadParser, JSONParser
from rest_framework import response
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse, HttpResponse
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
# from rest_condition import Or
from rest_framework import permissions, status
# Create your views here.


from django.conf import settings
import redis
import json

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0, decode_responses=True)

stop_words = ['a','also','an','and','are','as','at','be','because','been','but','by','for','from','has','have','however',
'if','in','is','not','of','on','or','p','so','than','that','the','their','there','these','this','to',
'was','were','whatever','whether','which','with','would']

def Getvaluesforsearch(request, searchkeys):
    searchkeylist = searchkeys.split()
    searchresult=set()

    #search for keys in users search criteria
    for searchkey in searchkeylist: 
        searchvalues = set(redis_instance.keys('*'+ searchkey+'*'))
        searchresult.update(searchvalues)
        searchvalues = set(redis_instance.keys('article:'+ searchkey+'*'))
        searchresult.update(searchvalues)
        searchvalues = set(redis_instance.keys('comments:'+ searchkey+'*'))
        searchresult.update(searchvalues)
    
    users = set()
    articles = set()
    comments = set()
    userslist = []
    postslist = []
    commentslist = []
    for redis_key in searchresult:
        type_key = redis_instance.type(redis_key)
        if type_key =='set':    # check whether it is of type set
            keys = redis_instance.smembers(redis_key)  # get all the hashkeys
            for key in keys:  # take each value from the set and put it in the respective model set
                if 'article:' in redis_key:
                    articles.add(key)
                elif 'comments:' in redis_key:
                    comments.add(key)
                else:
                    users.add(key)
                # redis_instance.smembers(key)
    if request.user.is_superuser:
        for userid in users:
            val = redis_instance.hgetall('users:'+ str(userid)) 
            userslist.append(val)
    for postid in articles:
        val = redis_instance.hgetall('posts:'+ str(postid)) 
        postslist.append(val)
    for commentid in comments:
        val = redis_instance.hgetall('comments:'+ str(commentid)) 
        commentslist.append(val)
    
    return {'userslist' : userslist, 'postlist' : postslist, 'commentslist': commentslist}

def usersearch(data, id, smethod, search):
    fname = data.get('first_name')
    lname = data.get('last_name')
    full_name = data.get('full_name')
    email = data.get('email')
    fname_response = redis_instance.sadd(fname, id)
    lname_response = redis_instance.sadd(lname, id)
    fullname_response = redis_instance.sadd(full_name, id)
    email_response = redis_instance.sadd(email, id)
    
def postsearch(data, id, parentid, smethod, search):
    document = 'articleset:' + str(parentid)
    redis_instance.sadd(document, id)  # create a articleset:userid and add the article id's
    title=data.get('title')
    subtitle=data.get('subtitle')
    content=data.get('content')  
    title_response = redis_instance.sadd('article:'+title, id)
    subtitle_response = redis_instance.sadd('article:'+ subtitle, id)
    splitstring = (content.split())   # split the content
    resultstring = [word for word in splitstring if word.lower() not in stop_words]
    for s in resultstring:
        redis_instance.sadd('article:'+ s, id)

def commentsearch(data, id, parentid, smethod, search):
    document = 'commentset:' + str(parentid)
    redis_instance.sadd(document, id)  # create a commentset:articleid and add the article id's
    content=data.get('content') 
    splitstring = (content.split())   # split the content
    resultstring = [word for word in splitstring if word.lower() not in stop_words]
    for s in resultstring:
        redis_instance.sadd('comments:'+ s, id)

def GetUpdateRedisData(data, id, model, mtype, parentid):
    print('data.....', f'{data}')
    # return type(f'{data}')
    if id !="":
        try:
            document = str(model)+ ":" + str(id)
            if mtype =='createorupdate':
                redis_response = redis_instance.sadd(model, id)     # added the Id to list of users                
                print(document)
                print(data)
                redis_response = redis_instance.hmset(document, data) # create or modify the user hash table
                if model == 'users':
                    usersearch(data, id, 'update', '')  
                elif model == 'posts':
                    postsearch(data, id, parentid, 'update', '')
                elif model =='comments':
                    commentsearch(data, id, parentid, 'update', '')

                if redis_response:
                    return redis_instance.hgetall(document)
                else:   
                    response = JsonResponse({
                            "error": {
                                "code" : 404,
                                "message" : "Record not found in search engine"
                            }})
                    return response
            if mtype =='read':
                # return json.dumps(redis_instance.hgetall(document), indent=4)
                value = redis_instance.hgetall(document)
                if model == 'posts':
                    commentskey = "commentset:" + str(id)
                    comments_set_ids =  redis_instance.smembers(commentskey)
                    comments_set =[]
                    for comment in comments_set_ids:
                        commentval = redis_instance.hgetall('comments:'+ comment)
                        comments_set.append(commentval)
                    value['comments_set'] = comments_set
                return value
        except:
            response = JsonResponse({
                            "error": {
                                "code" : 400,
                                "message" : "Error updating or reading the records"
                            }})
            return response 
    else:
        model_ids = redis_instance.smembers(model)
        i=0
        responses = []
        for id in model_ids:            
            document = str(model)+ ":" + str(id)
            response = redis_instance.hgetall(document)
            responses.append(response)
        return responses

class ListCreateUserView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = (DjangoFilterBackend,OrderingFilter, SearchFilter)
    parser_classes = [MultiPartParser, JSONParser,FileUploadParser]
    filterset_fields = ('last_name', 'email')
    ordering_fields = ('last_name', 'first_name')
    search_fields = ('first_name', 'last_name', 'email', 'username')
    def get(self, *args, **kwargs):
        response = GetUpdateRedisData('', '', 'users', 'read', '')        
        return Response(response)
        # return super().get(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        print(request.data)
        # file_obj = request.data['file']
        # print('....................................', file_obj)
        # if request.data['file']:
        #     image_file_obj = request.data.get('file')
        # serializer = UserSerializer(data=request.data  , files=request.FILES)
        serializer = UserSerializer(data=request.data)
        # profileserializer = ProfileSerializer(data=request.data)
        # if profileserializer.is_valid():
        #     image = profileserializer.data.image
        # print('---------------------------', serializer)
        if serializer.is_valid():
            serializer.save()            
            redis_data = serializer.data
            del redis_data['profile']
            # redis_data['image_field'] =image
            # profiledoc = Profile.objects.get(user=)
            # if profiledoc is not None:
            #     print(profiledoc.image)
            response = GetUpdateRedisData(redis_data, redis_data.get('id'), 'users', 'createorupdate', '')
            return Response(response)
            # return Response({'received data': request.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        response = super().update(request, *args, **kwargs)
        response = GetUpdateRedisData(response.data, response.data.get('id'), 'users', 'createorupdate', '')
        print(response)
        return response

    def perform_update(self, serializer):
        content = JSONRenderer().render(serializer.validated_data)
        print(self.request.POST.get('pk'))
        print('content............', content)

        return super().perform_update(serializer)
    
    def get(self, *args, **kwargs):
        print('inside get method')
        print(kwargs.get('pk'))        
            
        response = GetUpdateRedisData('', kwargs.get('pk'), 'users', 'read', '')
        # return HttpResponse(response, content_type="application/json")
        print('response............', response)
        # return JSONRenderer().render(response)
        return Response(response)
        # return super().get(*args, **kwargs)

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
    # parser_classes = [MultiPartParser, JSONParser,FileUploadParser]
    filter_backends = (DjangoFilterBackend,OrderingFilter, SearchFilter)
    filterset_fields = ('title','content','subtitle', 'published_at','author')
    ordering_fields = ('title','content','subtitle', 'published_at','author')
    search_fields = ('title','content','subtitle')
    
    def get(self, *args, **kwargs):
        # return super().get(*args, **kwargs)
        response = GetUpdateRedisData('', '', 'posts', 'read', '')        
        # return response
        return Response(response)

    def perform_create(self, serializer):        
        serializer.save(author=self.request.user)
    
    def post(self, *args, **kwargs):
        serializer = UserSerializer(data=self.request.data)
        response= super().post(*args, **kwargs)
        print(response.data)       
        del response.data['comments_set']
        response = GetUpdateRedisData(response.data, response.data.get('id'), 'posts', 'createorupdate', request.user.id)
        return Response(response)
        # return super().post(*args, **kwargs)

class RetrieveUpdateDestroyPost(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrIsAdminOrReadOnly]

    
    def get(self, *args, **kwargs):
        print(kwargs.get('pk'))        
        # return super().get(*args, **kwargs)
            
        response = GetUpdateRedisData('', kwargs.get('pk'), 'posts', 'read', '')
        # return HttpResponse(response, content_type="application/json")
        print('response............', response)
        # return JSONRenderer().render(response)
        return Response(response)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        response= super().update(request, *args, **kwargs)                
        del response.data['comments_set']        
        userid = request.user.id
        response = GetUpdateRedisData(response.data, response.data.get('id'), 'posts', 'createorupdate', userid)        
        return response

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
        id = kwargs.get('pk')        
        
        response = super().update(request, *args, **kwargs)             
        activeflag = response.data['active']
        response.data['active'] = str(activeflag)        
        parent_id = kwargs.get('post_id')        
        response = GetUpdateRedisData(response.data, response.data.get('id'), 'comments', 'createorupdate', parent_id)        
        return response
    
        response= super().update(request, *args, **kwargs)                
        del response.data['comments_set']        
        userid = request.user.id
        response = GetUpdateRedisData(response.data, response.data.get('id'), 'posts', 'createorupdate', userid)        
        return response
    
    
    def get(self, *args, **kwargs):
        id = kwargs.get('pk')        
        parent_id = kwargs.get('post_id')
        return super().get(*args, **kwargs)
        response = GetUpdateRedisData('', kwargs.get('pk'), 'posts', 'read', '')
        print('response............', response)
        return Response(response)

class ApiSearch(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        search = request.query_params['search']
        result = Getvaluesforsearch(request, search)
        return Response(result)


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



