# ChatAPI 1.0

**Used Technology:**

1. Python
2. Django
3. Django Rest Framework
4. Django Channels
5. Redis
6. Heroku
7. Postgresql

**Live server link**

https://django-chat-api.herokuapp.com/

**Features**
    
1. Send message to a particular user
2. Updates Inbox when someone sends a new message
3. Updates status to online when a user logs in and updates status to offline when logs out
4. Can delete message
5. Paginated messages
6. Custom User Model


**Commands**

`python manage.py createsuperuser`  - To create superuser

`python manage.py collectstatic` - Collects Static

`python manage.py runserver`

**How to run on heroku**

1. Login to your heroku dashboard and create a Heroku App
2. Payment verify your account in order to use addons
3. Download and install heroku cli
4. Open terminal in the working directory and run the following commands in your terminal
5. Run `heroku login`, this will open a tab in your browser, click login
6. Run `heroku git:remote -a {your-app-name}`
7. Run `heroku addons:create heroku-postgresql:<PLAN_NAME>` -> if you want to buy any other plan
8. Run `heroku addons:create heroku-redis`
9. Run `heroku config:set SECRET_KEY="YOUR_SECRET_KEY" `
10. Run `heroku config:set FIELD_ENCRYPTION_KEYS="FIELD_ENCRYPTION_KEYS"`
11. Set database url in django settings
12. Run `git add .`
13. Run `git commit -m"Application setup"`
14. Run `git push heroku master`
15. Run `heroku run python manage.py migrate`


**Database Design**

![alt text](https://github.com/khan-asfi-reza/ChatAPI/blob/master/Media/design.png?raw=true)
