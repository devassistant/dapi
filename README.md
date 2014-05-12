Dapi on OpenShift
=================

This is Dapi - the DevAssistant Package Index.

It's Django app running on OpenShift using Python 2.7 and PostgreSQL 9.2 cartridges.

**This is currently in very experimental status and is not intended for production!**

Running on localhost
--------------------

If you want to run this on localhost for testing a development, follow those steps:

 1. Install python, pip, [virtualenv](https://pypi.python.org/pypi/virtualenv) and sqlite3 (in case you don't have it already)
 2. Clone the repo
 3. Open shell in the repo and run:

````
virtualenv venv
. venv/bin/activate
pip install -r requirements-local.txt
cd wsgi/
python manage.py syncdb --noinput
python manage.py migrate
python manage.py schemamigration dapi --initial
python manage.py migrate dapi --fake
mkdir upload
echo GITHUB-API-ID > github # see section Github tokens
echo GITHUB-API-SECRET >> github
python manage.py runserver
````

Keep the shell opened. Go to the URL that runserver tells you to go to, log in with Fedora or Github. Go back to the shell. Exit the server with Ctrl+C.

To make you an administrator:

```
python manage.py shell << EOM
from django.contrib.auth.models import User
u = User.objects.get(pk=1)
u.is_superuser = True
u.is_staff = True
u.save()
EOM
````

Use `python manage.py runserver` to run again. To deactivate your virtualenv environment, run `deactivate`.

To run the app next time, just open a shell in the cloned repo and run:

````
. venv/bin/activate
python wsgi/manage.py runserver
````

Deploying
---------

If you want to deploy this on OpenShift, follow those steps:

 1. Create Python 2.7 app on OpenShift (via web or `rhc`)
 2. Add PostgreSQL cartridge (via web or `rhc`)
 3. Clone this repository
 4. Create branch master
 5. Merge devel branch (or any other you want)
 6. `git remote add upstream -m master OPENSHIFT-GIT-URL # something like ssh://hexa@app-namespace.rhcloud.com/~/git/app.git/`
 7. Don't forget to update settings.py with your e-mail address, ALLOWED_HOSTS and SITE_URL.
 8. `git push openshift devel:master`
 9. ssh to the OpenShift app and run the following:

````
cd app-root/repo/wsgi/
python manage.py syncdb --noinput
python manage.py migrate
python manage.py schemamigration dapi --initial
python manage.py migrate dapi --fake
cp -r "${OPENSHIFT_REPO_DIR}wsgi/dapi/migrations" ${OPENSHIFT_DATA_DIR}
mkdir ${OPENSHIFT_DATA_DIR}upload
echo GITHUB-API-ID > ${OPENSHIFT_DATA_DIR}github # see section Github tokens
echo GITHUB-API-SECRET >> ${OPENSHIFT_DATA_DIR}github
````
Keep the ssh shell opened. Go to `http://website.url/`, log in with Fedora or Github. Go back to ssh shell.

To make you an administrator:

````
python manage.py shell << EOM
from django.contrib.auth.models import User
u = User.objects.get(pk=1) # or use (username=<username>) to be sure
u.is_superuser = True
u.is_staff = True
u.save()
EOM

````

Github tokens
-------------

Create a Github app as described in [python-socail-auth docs](http://psa.matiasaguirre.net/docs/backends/github.html).

Save Client ID and Client Secret to a simple plaintext file (first line ID, second line secret) and save it as `github`. On localhost, save the file to `wsgi/`, on Openshift, save the file to `$OPENSHIFT_DATA_DIR`. Use different key/secret combo for localhost and for Openshift. In the above doc those keys are referenced with GITHUB-API-ID and GITHUB-API-SECRET.
