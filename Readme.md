RC Event is designed to work on Heroku with the SendGrid and Scheduler addons.

If deploying to another site, be sure to use Postges version >= 9.4 and set these environmental variables:
'SENDGRID_USERNAME'
'SENDGRID_PASSWORD'


Set the TIME_ZONE in settings to your local time zone.
Set the DEFAULT_FROM_EMAIL to an email account you would like to be able to manage your calendars. Create a new gmail account for this, *do not* use your personal email address.

Save service account credentials in your project root directory as 'client_secret.json'. More information is available at: 
https://developers.google.com/identity/protocols/OAuth2ServiceAccount#creatinganaccount

Create a new secret key for your own deployment here
http://www.miniwebtool.com/django-secret-key-generator/



Installation Instructions:
2. Create a Heroku account. You will need to verify the account with a credit card.
    http://www.heroku.com

3. Install the Heroku toolbelt.
    https://toolbelt.heroku.com/

7. Install Git.
    https://git-scm.com/downloads

7. Type the following commands into a terminal window to download the source code and create the heroku app. Git will create whatever destination_directory you want.
    git clone https://github.com/Kienen/rcevent.git destination_directory
    heroku login
    heroku create your_app_name
    heroku addons:create sendgrid
    heroku buildpacks:set heroku/python

4. Create a new gmail account that will only be used for this project.
    http://www.gmail.com

5. Open the Service accounts section of the Developers Console's Permissions page.
    Go to https://console.developers.google.com/permissions/serviceaccounts?project=_

    Click Create service account.

    In the Create service account window, type a name for the service account and select Furnish a new private key. Selecting Grant Google Apps domain-wide authority to the service account does not do anything currently. Click Create, and save the private key file as "client_secret.json" in the directory that you created in step 4.

    Go to https://console.developers.google.com/apis/api/calendar/overview and click "enable".

6. Edit destination_directory/rcevent/settings.py with your favorite text editor. Change lines 218 and 219:
    SECRET KEY= "Cut/Paste secret key from http://www.miniwebtool.com/django-secret-key-generator/"
    DEFAULT_FROM_EMAIL= "the_email_address_from_step_4@gmail.com"



8. Type the following commands into the terminal window:
    git add .
    git commit -m "Deploying to Heroku"
    git push heroku master
    heroku run python manage.py migrate
    heroku run python manage.py createsuperuser 
        (The username doesn't matter, but use the email address you created in step 5)

9. Login to your new website at https://your_app_name.herokuapp.com!

10. Set up the site information:
    https://your_app_name.herokuapp.com/site/

    Use whatever name you want, but be sure to set the domain to your_app_name.herokuapp.com or no one else will be able to create an account.

11. Set up scheduled maintenance.
    Go to https://dashboard.heroku.com/apps and click on your app.
    In the add-ons search box type: "Heroku Scheduler" and provision it. Click the add-on to add the daily maintenance jobs.

    $ python manage.py send_newsletter
        This will check every day if it's time to send the newsletter. (It just checks todays date against "Next" in step 10.) Note that if you manually send the newsletter, it will not automatically send it again for at least a week.

    $ python manage.py cleanup
        This deletes old events from the database. It does not remove recurring events. It does not delete events from the Google Calendar.

12. 