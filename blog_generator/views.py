from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from pytube import YouTube # type: ignore
from django.conf import settings
import os
import assemblyai as aai # type: ignore
import openai
# from openai import OpenAI
from .models import BlogPost
import re


# Create your views here.
@login_required
def index(request):
    return render(request,'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']

        except (KeyError,json.JSONDecodeError):
            return JsonResponse({'error':'Invalid data sent'},status=400)
        
        # get yt link
        title = yt_title(yt_link)

        #get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error':'Failed to get transcript'},status=500)

        #Use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error':'Failed to generate blog article'},status=500)

        #Save blog article to database
        new_blog_article = BlogPost.objects.create(
            user = request.user,
            youtube_title = title,
            youtube_link = yt_link,
            generated_content = blog_content,
        )
        new_blog_article.save()

        #return blog article as a response
        return JsonResponse({'content':blog_content})
    else:
        return JsonResponse({'error':'Invalid request method'},status=405)
    
def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title


def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file,new_file)
    return new_file

def get_transcription(link):
    audio_file = download_audio(link)

    # api key from assembly ai
    aai.settings.api_key = "3fd299c683c141399d9d017b431bd9db"

    # create transcriber object
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    return transcript.text

def generate_blog_from_transcription(transcription):
    # client = OpenAI(
    #     api_key = "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"
    # )
    # openai.api_key = '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'
  
    # prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"
    error_msg = "You exceeded your current quota, please check your plan and billing details."
    response = "This is what was supposed to be an AI auto generated text but its what its men. I get do get an error of billing",error_msg
    # response = openai.Completion.create(
    #     # model = "gpt-3.5-turbo",
    #     # prompt = prompt,
    #     # max_tokens=1000
    # )

    # patns = response.replace(",","",())
    # print("Printed response....",patns)
    # generated_content = response.choices[0].text.strip()
    generated_content = response
    

    return generated_content

def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html",{'blog_articles':blog_articles})

# Display blog details per post
def blog_details(request,pk):
    blog_article_details = BlogPost.objects.get(id=pk)
    if request.user == blog_article_details.user:
        return render(request,'blog-details.html',{'blog_article_details':blog_article_details})
    else:
        return redirect('/')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_massage = "Invalid username or password"
            return render(request,'login.html',{'error_massage':error_massage})
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']
        if password == repeatPassword:
            try:
                user = User.objects.create_user(username,email,password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request,'signup.html', {'error_message':error_message})
        else:
            error_message = "Password do not match"
            return render(request,'signup.html', {'error_message':error_message})

    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')