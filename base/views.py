from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db.models  import Q

from .models import Room,Topic,Message
from django.contrib.auth.models import User
from .forms import RoomForm
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
# rooms =[ 
#     {'id':1 ,'name':'lets learn python'},
#     {'id':2 ,'name':'Design with me'},
#     {'id':3  ,'name':'Frontend Developer'}
    
# ]
# rooms = Room.objects.all()


# Create your views here.
def LoginPage(request):
    
    page = 'Login'
    
    # if user already login
    if request.user.is_authenticated:
        return redirect('home')
    
    # user login authentication
    if request.method =="POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = user.objects.get(username=username)
        except:
            messages.error(request,'user does not exist')
        user = authenticate(request,username=username,password=password)
        
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username or Password does not exist')
    context={'page':page}
    return render(request ,'base/login_register.html',context)

def LogoutUser(request):
    logout(request)
    return redirect('home')

def RegisterUser(request):
    page = 'register'
    form = UserCreationForm()
    
    # create a user and sign up a user
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            # error handle
            messages.error(request,'An error occurred during registration')
            
            
    context={'page':page,'form':form}
    return render(request,'base/login_register.html',context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)|
        Q(name__icontains=q)|
        Q(description__icontains=q)
        )
    # msg = Message.objects.filter(user__icontains=q)
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    
    topics = Topic.objects.all() 
    topic_count = topics.count()
    context = {'rooms':rooms,'topics':topics,'room_count':room_count,'topic_count':topic_count,'room_messages':room_messages}
    return render(request, 'base/home.html',context)

def room(request,pk):
   
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    partic = participants.count()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
        
    context = {'room':room,'room_messages':room_messages ,'participants':participants ,'partic':partic}
    return render(request,'base/room.html',context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html', context,)


@login_required(login_url='Login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        # form = RoomForm(request.POST)
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
            
        )
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')
    context ={'form':form,'topics': topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='Login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
      
        # restricting anybody for update a user room
    if request.user != room.host:
        return HttpResponse('you are not allow to be here!!')
    
    # checking validation
    if request.method == 'POST':   
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context ={'form':form, 'topics':topics,'room':room}
    return render(request,'base/room_form.html',context)


@login_required(login_url='Login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    
    # restricting anybody for update a user room
    if request.user != room.host:
        return HttpResponse('your are not allow here!!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context ={'obj':room}
    return render(request,'base/delete.html',context)


@login_required(login_url='Login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)
    
    # restricting anybody for update a user room
    if request.user != message.user:
        return HttpResponse('your are not allow here!!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context ={'obj':message}
    return render(request,'base/delete.html',context)

@login_required(login_url='Login')
def updateUser(request):
    user = request.user
    form = UserForm(request.POST,instance=user)
    context = {'form' : form}  
    if request.method == 'POST':
        form =UserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    

    return render(request,'base/update-user.html',context)