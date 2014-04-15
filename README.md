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
 3. Clone this repository
 4. Create branch master
 5. Merge devel branch (or any other you want)
 6. `git remote add upstream -m master OPENSHIFT-GIT-URL # something like ssh://hexa@app-namespace.rhcloud.com/~/git/app.git/`
 7. `git push openshift devel:master`
 8. ssh to the OpenShift app and run the following:

````
cd app-root/repo/wsgi/
./manage.py syncb # create admin user!
./manage.py migrate
./manage.py schemamigration dapi --initial
./manage.py migrate dapi --fake
cp -r "${OPENSHIFT_REPO_DIR}wsgi/dapi/migrations" ${OPENSHIFT_DATA_DIR}
mkdir ${OPENSHIFT_DATA_DIR}upload
echo GITHUB-API-ID > ${OPENSHIFT_DATA_DIR}github
echo GITHUB-API-SECRET >> ${OPENSHIFT_DATA_DIR}github
````

Don't forget to update settings.py with your e-mail address and ALLOWED_HOSTS.

Go to `http://website.url/admin`, log in as admin and add a Profile for your admin user! Feel free to disable admin on production.

Github tokens
-------------

Create a Github app as described in [python-socail-auth docs](http://psa.matiasaguirre.net/docs/backends/github.html).

Save Client ID and Client Secret to a simple plaintext file (first line ID, second line secret) and save it as `github`. On localhost, save the file to `wsgi/`, on Openshift, save the file to `$OPENSHIFT_DATA_DIR`. Use different key/secret combo for localhost and for Openshift. In teh above doc those keys are referenced with GITHUB-API-ID and GITHUB-API-SECRET.
