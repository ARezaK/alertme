# -*- coding: utf-8 -*-
import time
import requests
import smtplib
from custom_config import *
import tweepy
from datetime import datetime
from twilio.rest import Client


def send_email(user, pwd, recipient, url):  # snippet courtesy of david / email sending function
    SUBJECT = 'SITE UPDATED'  # message subject
    body = 'CHANGE AT ' + str(url)  # message body
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)  # start smtp server on port 587
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)  # login to gmail server
        server.sendmail(FROM, TO, message)  # actually perform sending of mail
        server.close()  # end server
        print '[+]Successfully sent email notification'  # alert user mail was sent
    except Exception, e:  # else tell user it failed and why (exception e)
        print "[-]Failed to send notification email, " + str(e)


def sendtweet(consumer_key, consumer_secret, access_token, access_token_secret, status_string):
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        api.update_status(status_string)
    except tweepy.error.TweepError:
        print "[-]Error, invalid or expired twitter tokens, visit http://apps.twitter.com to retrieve or refresh them"


def sendtext(message):
    print "[+]Sending text message...."
    try:
        twilioCli = Client(accountSID, authToken)
        twilioCli.messages.create(body=message, from_=twilioNumber, to=myNumber)
    except Exception, e:
        print "[-]Error " + e
    print("Sent text message")


def main():
    print "[+]Starting up monitor"
    print "[+]Email on change detect is set to " + str(notify)
    print "[+]Tweeting is set to " + str(tweet)
    print "[+]Text notifications set to " + str(text)

    while 1:
        for url in urls:
            print("stasrting URL", url)
            with requests.Session() as c:
                try:
                    page1 = c.get(url, headers=headers)  # base page that will be compared against
                except Exception, e:
                    print "[-]Error Encountered during initial page retrieval: " + e
                    continue

                time.sleep(wait_time)  # wait beetween comparisons
                try:
                    print('trying page 2')
                    page2 = c.get(url, headers=headers)  # page to be compared against page1 / the base page
                except Exception, e:
                    print "[+]Error Encountered during comparison page retrieval: " + e
                    continue

                if page1.content == page2.content:  # if else statement to check if content of page remained same
                    print '[-]No Change Detected on ' + str(url) + "\n" + str(datetime.now())
                else:
                    status_string = 'Change Detected at ' + str(url) + "\n" + str(datetime.now())
                    message = status_string
                    print "[+]" + status_string
                    if notify:
                        send_email(user, pwd, recipient, url)  # send notification email
                    else:
                        pass
                    if tweet:
                        sendtweet(consumer_key, consumer_secret, access_token, access_token_secret, status_string)
                    else:
                        pass
                    if text:
                        sendtext(message)
                    time.sleep(4800)


if __name__ == '__main__':
    main()
