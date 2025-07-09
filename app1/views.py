from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from app1.langchain import func
from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
import requests
from decouple import config
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
pixabay_api = config('pixal_bay_api')


@csrf_exempt
@api_view(['POST'])
def register(request):
    form = UserCreationForm(request.data)
    if form.is_valid():
        user = form.save()
        return Response({'success': True, 'message': 'User registered successfully'})
    else:
        return Response({'success': False, 'errors': form.errors})

   

@csrf_exempt
@api_view(['POST'])
def user_login(request):
    form = AuthenticationForm(data=request.data)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return Response({'success': True, 'message': 'Login successful'})
    else:
        return Response({'success': False, 'errors': form.errors})
    
@api_view(['POST'])
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return Response({'success': True, 'message': 'Logout successful'}, status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'message': 'User not logged in'}, status=status.HTTP_400_BAD_REQUEST)



def get_images(query):
    params = {
        "key": pixabay_api,
        "q": f"{query} food",
        "category": "food",
        "image_type": "photo",
        "safesearch": "true",
        "per_page": 5
    }
    try:
        response = requests.get("https://pixabay.com/api/", params=params)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("hits", []):
                tags = item.get("tags", "").lower()
                if not any(x in tags for x in ['live']):
                    return item.get("webformatURL")

    except requests.RequestException as e:
        print(f"Pixabay API request failed: {e}")
    return "https://dummyimage.com/600x400/cccccc/ffffff&text=No+Image" 



@api_view(['GET','POST']) 
def home(request):
    if request.method == 'POST':
        try:
            fromuser = request.data.get('required_data','').strip()
            if not fromuser:
                return Response({
                    'success': False,
                    'error': 'Input data cannot be empty.'
                }, status=400)
            llm_response = func(fromuser)
            if not llm_response:
                return Response({
                    'success': False,
                    'error': 'Could not process the request. Please try a different query.'
                })
            convert_to_py = [item.model_dump() for item in llm_response]
            for item in convert_to_py:
                if isinstance(item, dict):
                    name = item.get("item_name")
                    image_link = get_images(name)
                    item['imageURL'] = image_link
            request.session['save_in_session'] = json.dumps(convert_to_py)          
            return Response({
                'success': True,
                'data': convert_to_py
            })
        except Exception as e:           
            print(f"An unexpected error occurred: {e}")
            return Response({
                'success': False,
                'error': f'An unexpected error occurred. Please check the server logs.'
            }, status=500)

    elif request.method == 'GET':
        session_data = request.session.get('save_in_session', None)
        if session_data:
            try:
                final_data = json.loads(session_data)
                return Response({
                    'success': True,
                    'data': final_data
                })
            except json.JSONDecodeError:
                return Response({
                    'success': False,
                    'error': 'Failed to load data from session.'
                })

        else:
            return Response({'success': False, 'message': 'No session data found.'}) 