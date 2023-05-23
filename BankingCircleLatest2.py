from datetime import datetime
from bs4 import BeautifulSoup
import requests, os
import pandas as pd
import os,json

GENERAL_WEBHOOK_SECRET_DEV="*****"
HOOK_URL = "https://hooks.slack.com/services/%s" % GENERAL_WEBHOOK_SECRET_DEV
current_dateTime = str(datetime.now()).split(" ")[0].split("-")[2]
nl = '\n'

class BankingCircle:
    
    def __init__(self, link):
        self.link = link
        self.soup = BeautifulSoup(requests.get(self.link).text, 'html.parser')
        self.incident_detected = []
        
    def get_link(self):
        return self.link
    
    def detect_incident(self):
        
        def to_string(data):
            return data.string
        
        incident_content=self.soup.find_all("div", class_="status-day font-regular")
        incident_comments=incident_content[0].find_all("span", class_="whitespace-pre-wrap")
        incident_status=incident_content[0].find_all("strong")
        date=to_string(self.soup.find_all("small")[0].find_all("var", "var-data"=="date")[0])
        month=str(self.soup.find_all("div", class_="date border-color font-large")).split(" ")[3].split(">")[1]

        for idx in range(len(incident_comments)):
            #if to_string(date) == current_dateTime and len(incident_status) >= 1:
            if to_string(date) == "16" and len(incident_status) >= 1:
                comments=[]
                time=incident_content[0].find_all("small")[idx].find_all("var", "var-data"=="date")[1]
                year=incident_content[0].find_all("div", class_="date border-color font-large")[0].find_all("var", "var-data"=="year")[1]
                if incident_comments[idx].string != None:
                    comments.append([to_string(incident_status[idx]),
                                     month,
                                     date,
                                     to_string(time),
                                     to_string(year),
                                     to_string(incident_comments[idx])])
            
                elif incident_comments[idx].string == None:
                    comments.append([to_string(incident_status[idx]),
                                     month,
                                     date,
                                     to_string(time),
                                     to_string(year),
                                     str(incident_comments[idx]).split("</br></span>")[0].replace("<br>", f"{nl}").split(">")[1]])

                print(pd.DataFrame(comments[0]).T.rename(columns={0:"Status",
                                                                  1:"Month",
                                                                  2:"Date",
                                                                  3:"Time",
                                                                  4:"Year",
                                                                  5:"Comments"}))
        
        return comments[0]


def prepare_notification_for_slack(data):
    slack_message = {'text': data, 'Attachment': "Notification! "}
    req = requests.post(HOOK_URL, json.dumps(slack_message))

def sending_incident_notificarion(data):
    if data != None:
        results = pd.DataFrame(data).T.rename(columns={0:"Status", 1:"Month", 2:"Date", 3:"Time", 4:"Year", 5:"Comments"})
        #prepare_notification_for_slack(f"<!subteam*****> BankingCircle Incident Notification {nl}{results}")
    
    else:
        print("No Incidents reported today!")
        
sending_incident_notificarion(BankingCircle('https://bankingcircleconnect.statuspage.io/#past-incidents').detect_incident())
