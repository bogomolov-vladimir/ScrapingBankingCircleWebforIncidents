from datetime import datetime
from bs4 import BeautifulSoup
import requests, os
import pandas as pd
import os,json

GENERAL_WEBHOOK_SECRET_DEV="**************************************"
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
        results_incidents_containers_list = self.soup.find_all("div", class_="incidents-list format-expanded")
        for element in results_incidents_containers_list:
            validating_for_incident_recodrs =str(element.find_all("strong")[0]).split("<")[1].split(">")[0]
            if "strong" in validating_for_incident_recodrs:
                incident_statuses = element.find_all("strong")[0].string
                incident_date_parse=str(element.find_all("small")[0]).split(" ")
                incident_date=incident_date_parse[14].split(">")[1].split("<")[0]
                var_data=element.find_all("small")[0].find_all("var", "var-data"=="date")
                if incident_date == current_dateTime:
                    self.incident_detected.append([incident_statuses,
                                                   incident_date_parse[12],
                                                   var_data[0].string,
                                                   var_data[1].string,
                                                   str(datetime.now()).split(" ")[0].split("-")[0],
                                                   element.find_all("span", class_="whitespace-pre-wrap")[0].string])
                                                   
                    return self.incident_detected[0]

def prepare_notification_for_slack(data):
    slack_message = {'text': data, 'Attachment': "Notification! "}
    req = requests.post(HOOK_URL, json.dumps(slack_message))

def sending_incident_notificarion(data):
    if data != None:
        results = pd.DataFrame(data).T.rename(columns={0:"Status", 1:"Month", 2:"Date", 3:"Time", 4:"Year", 5:"Comments"})
        prepare_notification_for_slack(f"<!subteam****************> BankingCircle Incident Notification {nl}{results}")

sending_incident_notificarion(BankingCircle('https://bankingcircleconnect.statuspage.io/#past-incidents').detect_incident())