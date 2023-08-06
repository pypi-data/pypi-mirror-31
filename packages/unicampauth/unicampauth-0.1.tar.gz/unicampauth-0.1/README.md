Quick start
-----------
1. Add `unicampauth` to your `requirements.txt`

2. Add `maro_auth` to the _end_ of your INSTALLED_APPS setting like this::
    ```Python
    INSTALLED_APPS = [
        ...
        'unicampauth',
    ]
    ```

3. Include the URLconf in your project urls.py like this::

    `path('auth/', include('unicampauth.urls')),`

4. Run `python manage.py migrate` to create the auth models.

5. Add the following settings to your `settings.py` to configure the app:

    ```Python
    INDEX_URL_NAME = 'index'  # name of your project's index url. Used on redirects

    SITE_URL = 'http://localhost:8000'  # your site's url, without the '/' at the end. Used on emails

    UNICAMP_AUTH_APP_NAME = 'unicampauth'  # (optional) the name of the app containing your Auth Profile model

    UNICAMP_AUTH_MODEL_NAME = 'GoogleAuthProfile'  # (optional) the name of the Auth Profile model you'll want to use and associate with your Users

    GOOGLE_CLIENT_ID = '' # Google client ID for your application (only if using GoogleAuthProfile)

    GOOGLE_SECRET = '' # Google client secret for your application (only if using GoogleAuthProfile)

    GOOGLE_SCOPE = '' # Google scopes for your application (only if using GoogleAuthProfile)

    UNICAMP_AUTHENTICATOR_CLASS = 'unicampauth.authenticators.GooglePeopleAuthentication'  # (optional) path to the authenticator class to be used when authenticating users

    UNICAMP_VALIDATOR_CLASS = 'unicampauth.validators.GUnicampValidator'  # (optional) path to the validator class to be used when validating new users

    UNICAMP_AUTH_FAIL_MESSAGE = '' # (optional) message to be displayed when the authentication or validation fails
    ```
