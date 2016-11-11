# likes
Исходный код для Django приложения.

Подсчет лайков на стене за выбранный период

# Форма для ввода ссылки и выбора даты:
<img src="https://habrastorage.org/files/78e/428/63e/78e42863e0604fe090feb271443144bd.png"/>

# Результат:
<img src="https://habrastorage.org/files/0bf/912/cfd/0bf912cfd3324c29bfc853d2f1acc534.png"/>

# Install

1. Создаем прилоежние для Django, добавляем его в settings:
2. В urls прописываем, (like имя вашего приложения):
```python
from like.likes import *

urlpatterns = [
  url(r'^', include('like.urls')),
]
```
3. В settings добавить место хранения сессий:
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
```
4. template и static перемещаем в ваши папки где хранятся шаблоны и статика:
