import toml 
import requests, requests.cookies
import http.cookiejar as cookielib
from bs4 import BeautifulSoup
import apprise
import shelve
from typing import Dict, cast
from io import StringIO
from time import sleep
import logging

def main():
    config = loadConfig()

    logLevel = getattr(logging, config['logLevel'].upper())
    logging.basicConfig(format="%(asctime)s %(message)s", level=logLevel)

    checkInterval = config['checkInterval'] * 60

    while True:
        logging.info("Checking for notifications...")
        newNotifs = getNewNotifications(config)

        logging.debug(f"New notifs: {newNotifs}")

        if len(newNotifs) > 0:
            logging.info("Found new notifications, sending message...")

            msg = buildNotificationMessage(newNotifs)
            subj = "FA Notify - New FA Notifications"
            sendNotification(subj, msg, config['notificationUrl'])

            logging.info("Message sent")
        
        sleep(checkInterval)

def getNewNotifications(config):
    session = createRequestSession(config['userAgent'], config['cookieFile'])
    currentNotifs = getNotifications(session)
    oldNotifs = loadOldNotifications(config['shelveFile'])

    logging.debug(f"Notifications reported by FA: {currentNotifs}")
    logging.debug(f"Notifications from last check: {oldNotifs}")

    # only report notifications that have *changed*, are non-zero, are are ones
    # we've opted into
    newNotifs = {}
    for (k, v) in currentNotifs.items():
        if v > 0 and v != oldNotifs[k] and k in config['notifyOn']:
            newNotifs[k] = v
    
    # update the db
    saveNotifications(config['shelveFile'], currentNotifs)

    # return new notifications
    return newNotifs

def loadConfig():
    try:
        return toml.load('config.toml')
    except Exception as e:
        msg = "Failed to load the config file. \n" \
            + "If this is your first time running this program, " \
            + "edit config_example.toml to your needs and rename it " \
            + "to 'config.toml'"

        print(msg)
        print()
        print(e)
        exit(1)

def createRequestSession(userAgent: str, cookieFile: str):
    session = requests.session()
    session.headers.update({'User-Agent': userAgent})

    cookies = cookielib.MozillaCookieJar(cookieFile)
    cookies.load()

    session.cookies = cast(requests.cookies.RequestsCookieJar, cookies)
    return session

def getNotifications(s: requests.Session):
    resp = s.get("https://www.furaffinity.net")
    if resp.status_code != 200:
        print("Failed to load furaffinity.")
        exit(1)
    
    return extractNotifications(resp.text)

def extractNotifications(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    notifLinks = soup.find_all("a", class_="notification-container inline")

    notifs = getEmptyNotifDict()

    for l in notifLinks:
        link: str = l.attrs['href'] #type: ignore
        cnt = int(l.string[:-1]) #type: ignore #chop off the last letter

        if "submissions" in link: 
            notifs["submissions"] = cnt
        elif "watches" in link:
            notifs["watches"] = cnt
        elif "comments" in link:
            notifs["comments"] = cnt
        elif "favorites" in link:
            notifs["favorites"] = cnt
        elif "journals" in link:
            notifs["journals"] = cnt
        elif "pms" in link:
            notifs["notes"] = cnt

    return notifs

def getEmptyNotifDict():
    return {
        "submissions": 0,
        "watches": 0,
        "comments": 0,
        "favorites": 0,
        "journals": 0,
        "notes": 0
    }

def loadOldNotifications(shelveFile: str):
    #note if this is a fresh db
        
    with shelve.open(shelveFile) as db:
        if 'notifs' in db: 
            return db['notifs']

        else: return getEmptyNotifDict()

def saveNotifications(shelveFile: str, notifs: Dict[str, int]):
    with shelve.open(shelveFile) as db:
        db['notifs'] = notifs

def sendNotification(subj: str, msg: str, notifUrl: str):
    apobj = apprise.Apprise()
    apobj.add(notifUrl)

    apobj.notify(
        body=msg,
        title=subj
    )

def buildNotificationMessage(newNotifs: Dict[str, int]):
    s = StringIO("Hi there. You have new notifications on FurAffinity!\n\n")
    for (k,v) in newNotifs.items():
        key = f"New {k}:"
        s.write(f"{k:15}: {v}\n")

    return s.getvalue()

if __name__ == '__main__':
    main()