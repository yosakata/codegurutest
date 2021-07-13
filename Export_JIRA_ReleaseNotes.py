import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import json
import re
import os


class exportBugList:
   def __init__(self):
      self.query = ''
      self.startAt = 0
      self.maxResult = 50
      self.filename = ''
   
   def exportQuery(self):
      itemList = []
      f = open(self.filename, "w")
      
      header = "|Domain|Issue Key|Summary|Affect Version|\n|---|---|---|---|\n"
      while True:
         url = "https://nuancecommunications.atlassian.net/rest/api/2/search?maxResults=" + str(self.maxResult) + "&startAt=" + str(self.startAt) + "&jql=" + urllib.parse.quote(self.query)  

         # Add admin credentials
         auth = HTTPBasicAuth(AdminEmail, AdminToken)

         headers = {
            "Accept": "application/json"
         }
         response = requests.request(
            "GET",
            url,
            headers=headers,
            auth=auth
         )
         results = json.loads(response.text)
         total = results["total"]
         for issue in results["issues"]:
            output = ''
            if issue["fields"]["customfield_10027"] is not None:
               output = output + "|" + issue["fields"]["customfield_10027"][0]["value"] + "|"
            else:
               output = output + "|-|"
            output = output + issue["key"] + "|"
            if issue["fields"]["summary"] is not None:
               # clean up Summary
               tmp = re.sub('["|]', '', issue["fields"]["summary"])
               tmp1 = re.sub('^\w+?:', '', tmp)
               tmp2 = re.sub('^\[\w+?\]:*', '', tmp1)
               tmp3 = re.sub('^SW[0-9]+\(\w+?\):*', '', tmp2)
               summary = re.sub('^\W+', '', tmp3)
               output = output + summary + "|"
            else:
               output = output + "-|" 
            if len(issue["fields"]["versions"]) > 0:
               output = output + issue["fields"]["versions"][0]["name"] + "|\n"
            else:
               output = output + "-|\n"
            itemList.append(output)
         self.startAt = self.startAt + self.maxResult
         if self.startAt > total:
            break
      itemList.sort()
      f.write(header)
      for each in itemList:
         f.write(each)
      f.close()


fixVersion = 'SW10.1'
ebl_closed = exportBugList()
ebl_closed.filename = '0_closed_bug_' + fixVersion + '.txt'
ebl_closed.query = 'type = bug and fixVersion in (' + fixVersion + ') and ((status = closed) or (status = resolved and assignee not in membersOf(jira-nuance-users)))'
ebl_closed.exportQuery()

fixVersion = 'SW10, SW10.1'
ebl_resolved = exportBugList()
ebl_resolved.filename = '0_resolved_bug_' + fixVersion + '.txt'
ebl_resolved.query = 'type in (bug, defect) and status = resolved and fixVersion in (' + fixVersion + ')'
ebl_resolved.exportQuery()

ebl_open = exportBugList()
ebl_open.filename = '0_open_bug.txt'
ebl_open.query = 'type in (bug, defect) and status not in (closed, resolved, Triage, "External Triage", "Internal Triage") and created <= "2020/02/14"'
ebl_open.exportQuery()
