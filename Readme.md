RC Event is designed to work on Heroku with the SendGrid addon.

If deploying to another site, be sure to set these environmental variables:
'SENDGRID_USERNAME'
'SENDGRID_PASSWORD'

Set the TIME_ZONE in settings to your local time zone.
Set the ADMIN_EMAIL_ADDRESS to an email account you would like to be able to manage your calendars.

Save service account credentials in your project root directory as 'client_secret.json'. Instructions to create a service account are available at: 
https://developers.google.com/identity/protocols/OAuth2ServiceAccount#overview

