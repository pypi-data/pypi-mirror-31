=====
Poll
=====

Poll is a complex poll creation app, to create dynamic polls.
The usage of it is to create a set of questions with optional 
predefined answers.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "poll" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'poll',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('poll/', include('poll.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/poll/ to participate in the poll.