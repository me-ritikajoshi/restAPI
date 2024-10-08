from django.shortcuts import render
from rest_framework import generics,permissions,mixins,status
from .models import *
from .serializers import PostSerializer,VoteSerializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

# Create your views here.
class PostList(generics.ListCreateAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)


class VoteCreate(generics.CreateAPIView):
    serializer_class=VoteSerializers
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        user=self.request.user
        post=Post.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(voter=user,post=post)
    
    def perform_create(self, serializer):
        if self.get_queryset().exists():
            raise ValidationError('You have already voted for this post')
        serializer.save(voter=self.request.user,post=Post.objects.get(pk=self.kwargs['pk']))

    def delete(self,request,*args,**kwargs):
        if self.get_queryset().exists() :
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('You never voted for this post')
        
class PostRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def delete(self,request,*args,**kwargs):
        post=Post.objects.filter(pk=kwargs['pk'],poster=self.request.user)
        if post.exists():
            return self.destroy(request,*args,**kwargs)
        else:
            raise ValidationError('You are not authorized to delete this post')
        

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data=JSONParser().parse(request)
            user=User.objects.create_user(username=data['username'], password=data['password'])
            user.save()
            token=Token.objects.create(user=user)
            return JsonResponse({'token': str(token)},status=201)
        except IntegrityError:
            return JsonResponse({'error':'Username already exists, Please try another one .'},status=400)
        
@csrf_exempt
def login(request):
    if request.method =='POST':
        data=JSONParser().parse(request)
        user=authenticate(request,username=data['username'], password=data['password'])

        if user is None:
            return JsonResponse({'error':'Email and password doesnot match'},status=400)
        else:
            try:
                token=Token.objects.get(user=user)
            except:
                token=Token.objects.create(user=user)
            return JsonResponse({'token' : str(token)}, status=200)
