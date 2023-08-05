# django-nctu-oauth

This package currently still in testing stage
## Setup
1. Register your app at [nctu oauth website](https://id.nctu.edu.tw/)

2. Install package from pip
```
    pip install django-nctu-oauth
```

3. Add package to django project
```
    NCTU_APP_REDIRECT_URI = 'your-redirect-url'
    NCTU_APP_CLIENT_ID = 'your-client-id'
    NCTU_APP_CLIENT_SECRET = 'your-secret-key'

    INSTALLED_APPS = [
        'django-nctu-oauth',
    ]
```
## Testing
```
    python -m test.test
```