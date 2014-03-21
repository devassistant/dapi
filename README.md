Dapi on OpenShift
=================

This is Dapi - the DevAssistant Package Index.

It's Django app running on OpenShift using Python 2.7 and PostgreSQL 9.2 cartridges.

**This is currently in very experimental status and is not intended for production!**

Deploying
---------

If you want to deploy this on OpenShift, follow those steps:

 1. Create Python 2.7 app on OpenShift (via web or `rhc`)
 2. Add PostgreSQL cartridge (via web or `rhc`)
 3. Clone the initial app and cd to the cloned directory
 4. `git remote add upstream -m devel git@github.com:hroncok/dapi.git`
 5. `git pull -s recursive -X theirs upstream devel`
 6. `git push`
 7. ssh to the OpenShift app
 8. `cd app-root/repo/wsgi/openshift/`
 9. Create initial migration checkpoint for South and admin user:

````
./manage.py schemamigration dapi --initial
./manage.py migrate dapi --fake
cp -r "${OPENSHIFT_REPO_DIR}wsgi/openshift/dapi/migrations" ${OPENSHIFT_DATA_DIR}
./manage.py createsuperuser --username=foo --noinput --email foo@bar.com
./manage.py changepassword foo
````
