# coding=utf-8
from datetime import datetime

import re
import requests
import time
from django import forms
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse

# Настройки
from django.template import loader

from wemin import settings

# Форма
class FormLike(forms.Form):
    uri = forms.CharField(label='Ссылка на ВК', widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'rows': '1',
            'style': 'resize:none'
        }))
    data = forms.DateField(label='Начиная с ', widget=forms.DateInput(
        attrs={
            'class': 'datepicker form-control',
            'placeholder': 'Выберете дату',
            'autocomplete': 'off'
        }))


# Функции
def authorize(request):
    code = request.GET.get('code')
    redirect_url = __get_redirect_url(request)

    response = (requests.get(
        'https://oauth.vk.com/access_token?client_id=%s&client_secret=%s&redirect_uri=%s&code=%s'
        % (settings.VK_CLIENT_ID, settings.VK_CLIENT_SECRET, redirect_url, code))).json()
    
    request.session['access_token'] = response['access_token']

    return redirect('likes')


def __get_redirect_url(request):
    redirect_url = "%s://%s%s" % (
        request.META['wsgi.url_scheme'], request.META['HTTP_HOST'], reverse('auth'))
    return redirect_url


def index(request):
    redirect_url = __get_redirect_url(request)

    t = loader.get_template('buttons.html')
    c = {'redirect_url': redirect_url}
    return HttpResponse(t.render(c, request))


def uri_manager(request):
    if request.method == 'POST':
        form = FormLike(request.POST)
        if re.findall('id', request.POST.get('uri')) == ['id']:  # если ссылка с id пользователя
            owner_id = re.sub('.*id', '', request.POST.get('uri'))

            wall_get = (requests.post(
                'https://api.vk.com/method/wall.get?access_token=%s&owner_id=%s&filter=all&v=5.59' % (
                    request.session['access_token'], owner_id))).json()
            users = __dubbing(request, wall_get, owner_id)

            return render(request, 'result.html', {'users': users})

        elif re.findall('club', request.POST.get('uri')) == ['club']:  # если ссылка с id группы пользователя
            owner_id = re.sub('.*club', '', request.POST.get('uri'))
            owner_id = '-%s' % owner_id
            wall_get = (requests.post(
                'https://api.vk.com/method/wall.get?access_token=%s&owner_id=%s&filter=all&v=5.59' % (
                    request.session['access_token'], owner_id))).json()
            users = __dubbing(request, wall_get, owner_id)

            return render(request, 'result.html', {'users': users})

        else:
            domain = re.sub('.*com', '', request.POST.get('uri')).split('/')  # если ссылка с именем вместо id
            owner_id = (requests.post(
                'https://api.vk.com/method/utils.resolveScreenName?screen_name=%s&v=5.59' % domain[1])).json()
            if owner_id['response']['type'] == 'group' or owner_id['response']['type'] == 'page':
                owner_id = '-%s' % owner_id['response']['object_id']
            else:
                owner_id = owner_id['response']['object_id']
            wall_get = (requests.post(
                'https://api.vk.com/method/wall.get?access_token=%s&owner_id=%s&filter=all&v=5.59' % (
                    request.session['access_token'], owner_id))).json()
            users = __dubbing(request, wall_get, owner_id)

            return render(request, 'result.html', {'users': users})
    else:
        form = FormLike()
        return render(request, 'like.html', {'form': form})


def __dubbing(request, wall_get, owner_id):
    # дата в unix формате
    date = int(
        time.mktime(datetime.strptime(request.POST.get('data'), '%d-%m-%Y').timetuple()))
    # выборка id записей стены начиная с выбранной даты
    i = 0
    wall = []
    for item in wall_get['response']['items']:
        if date <= item['date']:
            wall.append(item['id'])
        i += 1

    # подсчет лайков у каждой записи
    result = {}
    for item in wall:
        likes_get = (requests.post(
            'https://api.vk.com/method/likes.getList?access_token=%s&owner_id=%s&item_id=%s&type=post&extended=1&v=5.59' % (
                request.session['access_token'], owner_id, item))).json()
        if 'response' in likes_get and 'items' in likes_get['response']:
            for like in likes_get['response']['items']:
                if not like['id'] in result:
                    result[like['id']] = 0

                result[like['id']] += 1

    users = []
    for user_id, likes in result.items():
        user_info = (requests.post(
            'https://api.vk.com/method/users.get?access_token=%s&user_ids=%s&fields=photo_50&v=5.59' % (request.session['access_token'], user_id))).json()

        user = user_info['response'][0]
        user['likes'] = likes
        users.append(user)

    users = sorted(users, key=lambda x: x['likes'], reverse=True)
    return users
