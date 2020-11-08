# ChatAPI 1.0

**Used Technology:**

1. Python
2. Django
3. Django Rest Framework
4. Django Channels
5. Redis



**Features**
    
1. Send message to a particular user
2. Updates Inbox when someone sends a new message
3. Updates status to online when a user logs in and updates status to offline when logs out
4. Can delete message
5. Paginated messages
6. Custom User Model

**Database Design**

![alt text](https://github.com/khan-asfi-reza/ChatAPI/blob/master/Media/design.png?raw=true)

**Commands**

`python manage.py createsuperuser`  - To create superuser

`python manage.py collectstatic`

`python manage.py runserver`

_NB: Currently this application does not have any frontend service to demonstrate_