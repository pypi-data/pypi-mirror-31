====
Feedback
====

Simple app for feedback

Quick start
-----------

1. Add "feedback" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'feedback',
    ]

2. Include the feedback URLconf in your project urls.py like this::

    path('feedback/', include('feedback.urls'))

3. Run `python3 manage.py migrate` to create the feedback models.

4. Start the development server and visit http://127.0.01:8000/admin/ to create
   a feedback (you'll need the Admin app enabled).
