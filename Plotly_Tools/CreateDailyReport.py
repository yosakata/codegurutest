import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import json
import re
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly 
from plotly.subplots import make_subplots
from datetime import date, timedelta
import calendar
from time import time
from datetime import datetime 

archive_file_name = 'DailyReport_' + str(datetime.now().date) + '.aspx'

startAt = 0
maxResult = 50
totalMaxResult = 1
created_cum = 0
resolved_cum = 0
p1_pri = 'Blocker, "A(1) - Critical", "B(2) - High"'
sprints = {}
startDay = '2020-02-15'
endDay = '2020-02-25'
resource = 900

dayDict = {'date': [], 
             'Triage': [], 
             'Open': [], 
             'Blocked': [], 
             'In Progress': [], 
             'In Review': [], 
             'Resolved': [], 
             'Closed': [], 
             'Total': [], 
             'OrgTime': [], 
             'RemTime': [], 
             'EstOrgTime': [], 
             'EstRemTime': [],
             'EstRemTimeFuture': [],
             'table': []
             }

def getList(dict):
   return list(dict.keys())

def composeQuery(startDay, endDay, queryType, priority):
   if queryType == 'Created':
      return "type in (bug, defect) and created > " + startDay + " and created <= " + endDay + " and priority in (" + priority + ")"
   elif queryType == 'Resolved':
      return "type in (bug, defect) and status changed to resolved during (" + startDay + "," + endDay + ")" + " and priority in (" + priority + ")"
   elif queryType == 'Closed':
      return "type in (bug, defect) and status changed to closed during (" + startDay + "," + endDay + ")" + " and priority in (" + priority + ")"
   elif queryType == 'Open':
      return "type in (bug, defect) and status was not in (resolved, closed) during (" + startDay + "," + endDay + ")" + " And priority in (" + priority + ")"
   else:
      return ""

def getResultsFromJIRA(query, startAt, maxResult):
   time_before = time()
   url = "https://nuancecommunications.atlassian.net/rest/api/2/search?maxResults=" + str(maxResult) + "&startAt=" + str(startAt) + "&jql=" + urllib.parse.quote(query)  
   auth = HTTPBasicAuth("yohei.sakata@nuance.com", "kPUFi9F9v9LkUK8ZN5Dg4E96")
   headers = {
      "Accept": "application/json"
   }
   response = requests.request(
      "GET",
      url,
      headers=headers,
      auth=auth
   )
   time_after = time()
   #print(time_after-time_before)
   return json.loads(response.text)

def exportQuery(query, startAt, maxResult):
   remaining_time = 0
   original_time = 0
   while True:

      results = getResultsFromJIRA(query, startAt, maxResult)
      total = results["total"]
      output = ""
      
      for issue in results["issues"]:
         if issue["fields"]["timeestimate"] is not None:
            remaining_time = remaining_time + issue["fields"]["timeestimate"]
         else:
            output = "|-|"
         if issue["fields"]["timeoriginalestimate"] is not None:
            original_time = original_time + issue["fields"]["timeoriginalestimate"]
         else:
            output = output + "-" + "|"
         #print(output)
      startAt = startAt + maxResult
      if startAt > total:
         break
   print(remaining_time/3600)
   print(original_time/3600)

def getRemainingHours(query, startAt, maxResult):
   remaining_time = 0
   original_time = 0
   while True:
      results = getResultsFromJIRA(query, startAt, maxResult)
      total = results["total"]
      for issue in results["issues"]:
         if issue["fields"]["timeestimate"] is not None:
            remaining_time = remaining_time + issue["fields"]["timeestimate"]
         if issue["fields"]["timeoriginalestimate"] is not None:
            original_time = original_time + issue["fields"]["timeoriginalestimate"]
      startAt = startAt + maxResult
      if startAt > total:
         break
   return [round(remaining_time/3600), round(original_time/3600)]

def getIssueTotal(query, startAt, maxResult):
   results = getResultsFromJIRA(query, startAt, maxResult)
   return int(results["total"])

def getdayList(startDay, endDay):
   dayToAdd = 1
   dayList = [startDay]
   while True:
      nextDay = datetime.fromisoformat(startDay) + timedelta(days=dayToAdd)
      dayList.append(str(datetime.date(nextDay)))
      if datetime.date(nextDay) == datetime.date(datetime.fromisoformat(endDay)):
         break
      dayToAdd = dayToAdd + 1
   return dayList

def addBarToList(jiraCategory, lineColor):
   trace = go.Bar(x=dayDict['date'],
                y=dayDict[jiraCategory],
                xaxis='x', 
                yaxis='y',
                marker=dict(color=lineColor),
                text=dayDict[jiraCategory],
                textposition='auto',
                name=jiraCategory)
   return trace 

def addScatterToList(jiraCategory, lineColor, modetype, dashtype, xlist, ylist):
   trace = go.Scatter(x=xlist, 
              y=ylist,
              marker=dict(color=lineColor),
              mode=modetype,
              name=jiraCategory,
              xaxis='x', 
              yaxis='y',
              line=dict(color=lineColor, width=1, dash=dashtype),
              text=xlist,
              textposition="middle right"
              )
   return trace

def reformatDayList(dayList):
   newDayList = []
   for day in dayList:
      x = datetime.fromisoformat(day)
      newDayList.append(x.strftime("%b %d"))
   return newDayList

# Get Remaining Time at Day 1
query = 'type in (story) and status was "Open" on ' + startDay
RemTime = getRemainingHours(query, startAt, maxResult)[0]
print(RemTime)

#dayDict['table'].append(getList(dayDict))
traceList = []
RemTimeFuture = 0
curRemTime = 0

for day in getdayList(startDay, endDay):
   # Add day
   dayDict['date'].append(day)

   # Past
   if datetime.fromisoformat(day).date() <= datetime.now().date():
      # Add Total of Open issues to Open List on that day
      query = 'type in (story) and status was "Triage" on ' + day
      dayDict['Triage'].append(getIssueTotal(query, startAt, totalMaxResult))

      # Add Total of Open issues to Open List on that day
      query = 'type in (story) and status was "Open" on ' + day
      dayDict['Open'].append(getIssueTotal(query, startAt, totalMaxResult))

      # Add Total of Issues that are resolved on the day
      query = 'type in (story) and status was "Blocked" on ' + day
      dayDict['Blocked'].append(getIssueTotal(query, startAt, totalMaxResult))

      # Add Total of Issues that are In Progress on the day
      query = 'type in (story) and status was "In Progress" on ' + day
      dayDict['In Progress'].append(getIssueTotal(query, startAt, totalMaxResult))

      # Add Total of Issues that are In Progress on the day
      query = 'type in (story) and status was "In Review" on ' + day
      dayDict['In Review'].append(getIssueTotal(query, startAt, totalMaxResult))

      # Add Total of Issues resolved on the day
      query = 'type in (story) and status changed to resolved on ' + day
      dayDict['Resolved'].append(getIssueTotal(query, startAt, totalMaxResult)*-1)

      # Add Total of Issues closed on the day
      query = 'type in (story) and status changed to closed on ' + day
      dayDict['Closed'].append(getIssueTotal(query, startAt, totalMaxResult)*-1)

      # Total 
      query = 'type in (story) and status was not in (Resolved, closed) on ' + day
      total = getIssueTotal(query, startAt, totalMaxResult)
      dayDict['Total'].append(total)

      # Remaining Hours
      query = 'type in (story) and status was "Open" on ' + day
      EstTime = getRemainingHours(query, startAt, maxResult)
      dayDict['RemTime'].append(EstTime[0])
      dayDict['OrgTime'].append(EstTime[1])
      RemTimeFuture = EstTime[0]
   
   if datetime.fromisoformat(day).date() < datetime.now().date():
      # Add black point before today
      dayDict['EstRemTimeFuture'].append('')
   # Today
   else:
      dayDict['EstRemTimeFuture'].append(RemTimeFuture)
      RemTimeFuture = RemTimeFuture - resource

   # Add forecast Hours
   dayDict['EstRemTime'].append(RemTime)
   RemTime = RemTime - resource

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=False,
    vertical_spacing=0.1,
    specs=[[{"secondary_y": True}],
           [{"type": "table"}]]
)

fig.add_trace(addBarToList('Open', '#FECF0F'), row=1, col=1, secondary_y=False)
fig.add_trace(addBarToList('Triage', '#AAFE0F'), row=1, col=1, secondary_y=False)
fig.add_trace(addBarToList('In Progress', '#C8FE0F'), row=1, col=1, secondary_y=False)
fig.add_trace(addBarToList('In Review', '#4DFE0F'), row=1, col=1, secondary_y=False)
fig.add_trace(addBarToList('Blocked', '#FE280F'), row=1, col=1, secondary_y=False)
fig.add_trace(addBarToList('Closed', '#0F21FE'), row=1, col=1, secondary_y=False)
fig.add_trace(addBarToList('Resolved', '#010D18'), row=1, col=1, secondary_y=False)

fig.add_trace(addScatterToList('RemTime', '#BB99ff', 'lines+markers', 'solid', dayDict['date'], dayDict['RemTime']), row=1, col=1, secondary_y=True)
fig.add_trace(addScatterToList('EstRemTime', 'red', 'lines+markers', 'dot', dayDict['date'], dayDict['EstRemTime']), row=1, col=1, secondary_y=True)
fig.add_trace(addScatterToList('EstRemTimeFuture', '#EE99ff', 'lines+markers', 'dot', dayDict['date'], dayDict['EstRemTimeFuture']), row=1, col=1, secondary_y=True)
fig.add_trace(addScatterToList('Total', 'black', 'lines+markers', 'solid', dayDict['date'], dayDict['Total']), row=1, col=1, secondary_y=False)


headerList = ['date', 'Triage', 'Open', 'Blocked', 'In Progress', 'In Review', 'Resolved', 'Closed', 'Total', 'Org Time', 'Rem Time']
newDayList = reformatDayList(dayDict['date'])

fig.add_trace(go.Table(
    header=dict(values=headerList,
                line_color='darkslategray',
                fill_color='lightskyblue',
                align='center'),
    cells=dict(values=[newDayList, # 1st column
                       dayDict['Triage'],
                       dayDict['Open'],
                       dayDict['Blocked'],
                       dayDict['In Progress'],
                       dayDict['In Review'],
                       dayDict['Resolved'],
                       dayDict['Closed'],
                       dayDict['Total'],
                       dayDict['OrgTime'],
                       dayDict['RemTime']
                       ], 
               line_color='darkslategray',
               fill_color='lightcyan',
               align='center')), row=2, col=1)

axis=dict(
    showline=True,
    zeroline=True,
    showgrid=True,
    mirror=True,
    ticklen=4,
    gridcolor='#ffffff',
    tickfont=dict(size=10)
)

fig.update_layout(
    height=1000,
    showlegend=True,
    title_text="Sprint Analysis - Sprint 28",
    barmode='relative',
    xaxis1=dict(axis)
)

# Update the margins to add a title and see graph x-labels.
#fig.layout.margin.update({'t':50, 'b':100})

fig.update_yaxes(title_text="<b>Total Issues</b>", secondary_y=False)
fig.update_yaxes(title_text="<b>Remaining Hours</b>", secondary_y=True)
fig.update_xaxes(dtick=86400000.0)

#fig.layout.yaxis3.update({'anchor': 'x2'})
#fig.layout.yaxis3.update({'title': 'hours'})
#fig.layout.yaxis3.update({'side': 'right'})
fig.layout.yaxis.update({'range': [0, 3000]})
fig.layout.yaxis.update({'dtick': 200})
#fig.layout.yaxis3.update({'overlaying':"y2"})


plotly.offline.plot(fig, filename = 'DailyReport.aspx', auto_open=False)
plotly.offline.plot(fig, filename = archive_file_name, auto_open=False)


fig.show()


