from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Post, Comments

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('image',)

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    full_name = serializers.SerializerMethodField(method_name="get_full_name")
    # imagefield = serializers.ImageField()
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'full_name', 'email', 'password', 'profile')
        extra_kwargs = {'password' : {'write_only' : True}}
        
    def get_full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name) 

    def create(self, validated_data):
        profile = validated_data.pop('profile')
        print("creating profile........................................")
        profileimage = profile['image']
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        profileobj = Profile.objects.get(user=user)
        if profileobj is not None:
            profileobj.image=profileimage
            profileobj.save()
        else:
            profileobj=Profile.objects.create(image=profileimage)
        # for profile in profiles:
        #     profileimg = profile[0]
        #     profile.objects.create(user=user)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    # profile = ProfileSerializer()
    
    imagefield = serializers.SerializerMethodField(method_name= "get_user_image")
    full_name = serializers.SerializerMethodField(method_name="get_full_name")
    def get_full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name) 
    
    def get_user_image(self,obj):
        request = self.context.get('request')        
        if (obj.profile.image):
            return request.build_absolute_uri(obj.profile.image.url)
        return ""
        # return obj.profile.image.url

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'full_name', 'email', 'imagefield')
        # extra_kwargs = {'password' : {'write_only' : True}}

    def update(self, instance, validated_data):
        # profile = validated_data.pop('profile')   
        print('validated_data---', validated_data)     
        # profileimage = profile['image']
        response = super().update(instance, validated_data)
        return response

class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)  
    # post =   serializers.StringRelatedField(read_only=True)  
    class Meta:
        model = Comments
        fields = ('id', 'content', 'created_at', 'active','author')

class PostSerializer(serializers.ModelSerializer):
    author= serializers.StringRelatedField(read_only=True)    
    comments_set = CommentsSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ('id', 'title', 'imageURL','content','subtitle', 'published_at', 'author', 'comments_set')

class UserPostSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()    
    post_set= PostSerializer(many=True, read_only=True)
    # imagefield = serializers.ImageField()
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'profile', 'post_set')
