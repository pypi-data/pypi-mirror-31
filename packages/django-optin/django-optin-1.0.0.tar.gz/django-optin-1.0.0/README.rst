=====
OptIn
=====

OptIn is a simple Django app to manage User Preferences. For each
Category, Users can select Yes or No.

You set the Categories through the Admin panel

Detailed documentation is needs writing.

Quick start
-----------

1. Add "optin" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'optin',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('optin/', include('optin.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a Category (you'll need the Admin app enabled).

5. Add <a href="{% url 'optin:user_opt_selection' user.id %}">OptIns</a> 
   to a template to provide a link.  Please note, User must be logged in.

6. Visit http://127.0.0.1:8000/, Login and click link to set preferences.


Settings
--------

OptIn uses AUTH_USER_MODEL as the default user model.  It will default to
the Django User model if AUTH_USER_MODEL is not set in settings.py

OPTIN_SETTINGS_UPDATE_MESSAGE_BOOLEAN:
If True, on successful update of preferences the OPTIN_SETTINGS_UPDATE_MESSAGE
is presented to User (via django messages).
Default = True

OPTIN_SETTINGS_UPDATE_MESSAGE:
Message displayed to User if OPTIN_SETTINGS_UPDATE_MESSAGE_BOOLEAN set to True.
Default = 'Preferences Updated'