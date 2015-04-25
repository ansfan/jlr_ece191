### Installation
1. pip install django

2. In a directory, initialize by running:
	django-admin startproject mysite

3. Setup SQLite3 as default
	python manage.py migrate

4. Run server
	python manage.py runserver 8080

5.python manage.py startapp [name]

6. After creating an application we also need to tell Django that it should use it. 
We do that in the file settings.py

Find INSTALLED_APPS =(..) and add '[name]' onto it. 

For example, 
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'name'
)

7) Create the models in models.py

8) Create tables for your models in data base. python manage.py makemigrations [name]

9)Django prepared for us a migration file that we have to apply now to our database, 
type python manage.py migrate [name]

10) Open admin.py 

from django.contrib import admin
from .models import Post

admin.site.register(Post)

11) python manage.py runserver
12)  http://127.0.0.1:8000/admin/ should take you to a log in page

13) Create a super user

14)
