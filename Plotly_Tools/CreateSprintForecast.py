import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import json
import re
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly 
from plotly.subplots import make_subplots
import logging
from datetime import date, timedelta
import calendar
from time import time
from datetime import datetime

sprintData = {'Sprints': [], 
                 'Created': [], 
                 'Created_Est': [], 
                 'Created_Table': [], 
                 'Created_Cum': [],
                 'Created_Cum_Est': [], 
                 'Created_Cum_Table': [],
                 'Resolved': [], 
                 'Resolved_Est': [], 
                 'Resolved_Table': [], 
                 'Resolved_Cum': [], 
                 'Resolved_Cum_Est': [], 
                 'Resolved_Cum_Table': [], 
                 'Closed': [], 
                 'Closed_Est': [], 
                 'Closed_Table': [], 
                 'Closed_Cum': [], 
                 'Closed_Cum_Est': [], 
                 'Closed_Cum_Table': [], 
                 'Open': [], 
                 'Open_Est': [],
                 'Open_Table': [], 
                 'Open_Org_Est': [],
                 'Diff': [],
                 'Diff_Table': [],
                 'Diff_Est': []
                 }

p1_pri = 'Blocker, "A(1) - Critical"'
p1_pri = 'Blocker, "A(1) - Critical", "B(2) - High", "C(3) - Medium", "D(4) - Low"'

def getList(dict):
   return list(dict.keys())

def composeQuery(startDay, endDay, queryType, jiraType, priority):
   if queryType == 'Created':
      return 'type in (' + jiraType + ') and created > ' + startDay + ' and created <= ' + endDay + ' and priority in (' + priority + ')'
   elif queryType == 'Resolved':
      return 'type in (' + jiraType + ') and status changed to resolved during (' + startDay + ',' + endDay + ')' + ' and priority in (' + priority + ')'
   elif queryType == 'Closed':
      return 'type in (' + jiraType + ') and status changed to closed during (' + startDay + ',' + endDay + ')' + ' and priority in (' + priority + ')'
   elif queryType == 'Open':
      return 'type in (' + jiraType + ') and status was not in (resolved, closed) during (' + startDay + ',' + endDay + ')' + ' and priority in (' + priority + ')'
   else:
      return ""

def getResultsFromJIRA(query, startAt, maxResult):
   url = "https://nuancecommunications.atlassian.net/rest/api/2/search?maxResults=" + str(configData['maxResult']) + "&startAt=" + str(startAt) + "&jql=" + urllib.parse.quote(query)  
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
   return json.loads(response.text)

def getahrefLink(query, title):
   tmp = '<a href="https://nuancecommunications.atlassian.net/issues/?jql=' + urllib.parse.quote(query, '/,=') + '">' + str(title) + '</a>'
   return tmp

def getIssueTotal(query, configData):
   results = getResultsFromJIRA(query, configData['startAt'], configData['maxResultForTotal'])
   return results['total']

def getStartEndDate(startDay, start, end, period):
   d = {}
   current = start
   start_date = datetime.date(datetime.fromisoformat(startDay))
   while True:
      if current > end:
         break
      end_date = start_date + timedelta(days=(period-1))
      d[current] = {'start': str(start_date), 'end': str(end_date)}
      start_date = start_date + timedelta(days=period)
      current = current + 1
   return d

def getTotalSprintAvg(startDay, queryType, configData):
   start_date = datetime.date(datetime.fromisoformat(startDay))
   past_3Sprint_Date = start_date - timedelta(days=42)
   query = composeQuery(str(past_3Sprint_Date), str(start_date), queryType, 'Bug, Defect', p1_pri)
   print(query)
   total = getIssueTotal(query, configData)
   return int(round(int(total) / 3))

def getMedian(tlist):
   tlist.sort()
   n = len(tlist)
   if n % 2 == 0:
      median1 = tlist[n//2]
      median2 = tlist[n//2 - 1]
      median = (median1 + median2)/2
   else:
      median = tlist[n//2]
   return median 

def estimateFutureBugCount(sprint, sprints, configData):
   totalList = []
   i = 1
   while True:
      if i > 5:
         break
      tgtStart = datetime.date(datetime.fromisoformat(sprints[sprint]['start'])) - timedelta(days=14*i)
      tgtEnd = datetime.date(datetime.fromisoformat(sprints[sprint]['end'])) - timedelta(days=14*i)
      query = composeQuery(str(tgtStart), str(tgtEnd), 'Created', 'Bug, Defect', p1_pri)
      total = getIssueTotal(query, configData)
      totalList.append(total)
      i = i + 1
   return getMedian(totalList)

def estimateDailyBugFixCount(sprint, configData, sprints, priority, jiraStatus, team):
   # Get Past 3 Bugs Resolution Capacity
   bList = []
   i = 0
   while True:
      if i == 2:
         break
      query = composeQuery(str(sprints[sprint-i]['start']), str(sprints[sprint-i]['end']), jiraStatus, 'Bug, Defect', priority)
      total = getIssueTotal(query, configData)
      bList.append(total/configData['sprint_resource'][str(sprint)][team])
      i = i + 1
   return getMedian(bList)

def addScatterToList(jiraCategory, lineColor, modetype, dashtype, name, marker_symbol):
   trace = go.Scatter(x=sprintData['Sprints'], 
              y=sprintData[jiraCategory],
              marker=dict(color=lineColor),
              marker_symbol=marker_symbol,
              mode=modetype,
              name=name,
              xaxis='x', 
              yaxis='y',
              line=dict(color=lineColor, width=1, dash=dashtype),
              text=sprintData[jiraCategory],
              textposition="middle right"
              )
   return trace

def addBarToList(jiraCategory, lineColor, opacity):
   trace = go.Bar(x=sprintData['Sprints'],
                y=sprintData[jiraCategory],
                xaxis='x', 
                yaxis='y',
                marker=dict(color=lineColor),
                text=sprintData[jiraCategory],
                textposition='outside',
                opacity=opacity,
                name=jiraCategory)
   return trace 

def updateCoefficient(sprint, milestone, coefficient):
   if sprint == milestone:
      coefficient = 0.9
   elif sprint > milestone:
      coefficient = coefficient - 0.1
   if coefficient < 0.1:
      coefficient = 0
   return coefficient

def collectData(sprintData, sprints, Created_Bugs_Est, BugResolvedDaily, BugClosedDaily, totalOpen, configData, milestone, current):
   Open_Est = 0
   Created_Cum = 0
   Resolved_Cum = 0
   Closed_Cum = 0
   coefficient = configData['coefficient']

   for sprint in sprints:

      coefficient  = updateCoefficient(sprint, milestone, coefficient)

      # add Each sprint
      sprintData['Sprints'].append(sprints[sprint]['start'])
      
      # Before Sprint
      if sprint <= current:
         # Created
         Created_Query = composeQuery(sprints[sprint]['start'], sprints[sprint]['end'], 'Created', 'Bug, Defect', p1_pri)
         Created_Total = getIssueTotal(Created_Query, configData)

         # Created Accumulated 
         Created_Cum = Created_Cum + Created_Total

         # Resolved   
         Resolved_Query = composeQuery(sprints[sprint]['start'], sprints[sprint]['end'], 'Resolved', 'Bug, Defect', p1_pri)
         Resolved_Total = getIssueTotal(Resolved_Query, configData)

         # Resolved Accumulated
         Resolved_Cum = Resolved_Cum + Resolved_Total

         # Closed
         Closed_Query = composeQuery(sprints[sprint]['start'], sprints[sprint]['end'], 'Closed', 'Bug, Defect', p1_pri)
         Closed_Total = getIssueTotal(Closed_Query, configData)

         Closed_Cum = Closed_Cum + Closed_Total

         # Created - Resolved
         Diff = Created_Total - Resolved_Total
   
         # Open 
         Open_Query = composeQuery(sprints[sprint]['start'], sprints[sprint]['end'], 'Open', 'Bug, Defect', p1_pri)
         Open_Total = getIssueTotal(Open_Query, configData)
      
      # Before Current: Add Actual Data from JIRA
      if sprint < current:
         sprintData['Created'].append(Created_Total)
         sprintData['Created_Table'].append(getahrefLink(Created_Query, Created_Total))
         sprintData['Created_Est'].append('')

         sprintData['Created_Cum'].append(Created_Cum)
         sprintData['Created_Cum_Table'].append(Created_Cum)
         sprintData['Created_Cum_Est'].append('')

         sprintData['Resolved'].append(Resolved_Total)
         sprintData['Resolved_Table'].append(getahrefLink(Resolved_Query, Resolved_Total))
         sprintData['Resolved_Est'].append('')

         sprintData['Resolved_Cum'].append(Resolved_Cum)
         sprintData['Resolved_Cum_Table'].append(Resolved_Cum)
         sprintData['Resolved_Cum_Est'].append('')

         sprintData['Closed'].append(Closed_Total)
         sprintData['Closed_Table'].append(getahrefLink(Closed_Query, Closed_Total))
         sprintData['Closed_Est'].append('')

         sprintData['Closed_Cum'].append(Closed_Cum)
         sprintData['Closed_Cum_Table'].append(Closed_Cum)
         sprintData['Closed_Cum_Est'].append('')

         sprintData['Diff'].append(Diff)
         sprintData['Diff_Table'].append(Diff)         
         sprintData['Diff_Est'].append('')

         sprintData['Open'].append(Open_Total)
         sprintData['Open_Table'].append(getahrefLink(Open_Query, Open_Total))
         sprintData['Open_Est'].append('')

         # Add empty value to estimate list

      # At Current: Actual Data = Estimated Data
      elif sprint == current:
         # Created
         sprintData['Created'].append(Created_Total)
         sprintData['Created_Table'].append(getahrefLink(Created_Query, Created_Total))
         sprintData['Created_Est'].append(Created_Total)

         # Created Accumulated
         sprintData['Created_Cum'].append(Created_Cum)
         sprintData['Created_Cum_Table'].append(Created_Cum)
         sprintData['Created_Cum_Est'].append(Created_Cum)
         Created_Cum_Est = Created_Cum

         # Resolved
         sprintData['Resolved'].append(Resolved_Total)
         sprintData['Resolved_Table'].append(getahrefLink(Resolved_Query, Resolved_Total))
         sprintData['Resolved_Est'].append(Resolved_Total)

         # Resolved Accumulated
         sprintData['Resolved_Cum'].append(Resolved_Cum)
         sprintData['Resolved_Cum_Table'].append(Resolved_Cum)
         sprintData['Resolved_Cum_Est'].append(Resolved_Cum)
         Resolved_Cum_Est = Resolved_Cum

         # Closed
         sprintData['Closed'].append(Closed_Total)
         sprintData['Closed_Table'].append(getahrefLink(Closed_Query, Closed_Total))
         sprintData['Closed_Est'].append(Closed_Total)

         sprintData['Closed_Cum'].append(Closed_Cum)
         sprintData['Closed_Cum_Table'].append(Closed_Cum)
         sprintData['Closed_Cum_Est'].append(Closed_Cum)
         Closed_Cum_Est = Closed_Cum

         sprintData['Diff'].append(Diff)
         sprintData['Diff_Table'].append(Diff)
         sprintData['Diff_Est'].append(Diff)

         sprintData['Open'].append(Open_Total)
         sprintData['Open_Table'].append(getahrefLink(Open_Query, Open_Total))
         sprintData['Open_Est'].append(Open_Total)
         Open_Est = Open_Total

      else:
         Created_Bugs_Est = Created_Bugs_Est * coefficient
         sprintData['Created_Est'].append(round(Created_Bugs_Est))
         sprintData['Created_Table'].append(round(Created_Bugs_Est))         

         Created_Cum_Est = Created_Cum_Est + Created_Bugs_Est
         sprintData['Created_Cum_Est'].append(round(Created_Cum_Est))
         sprintData['Created_Cum_Table'].append(round(Created_Cum_Est))

         # Resolved
         dev_team_capacity = configData['week_resource'][str(sprint)]['UI']
         
         Resolved_Bugs_Est = BugResolvedDaily * dev_team_capacity
         sprintData['Resolved_Table'].append(round(Resolved_Bugs_Est))
         sprintData['Resolved_Est'].append(round(Resolved_Bugs_Est))

         Resolved_Cum_Est = Resolved_Cum_Est + Resolved_Bugs_Est
         sprintData['Resolved_Cum_Table'].append(round(Resolved_Cum_Est))
         sprintData['Resolved_Cum_Est'].append(round(Resolved_Cum_Est))

         # Closed
         qa_team_capacity = configData['week_resource'][str(sprint)]['QA']

         Closed_Bugs_Est = BugClosedDaily * qa_team_capacity
         sprintData['Closed_Table'].append(round(Closed_Bugs_Est))
         sprintData['Closed_Est'].append(round(Closed_Bugs_Est))

         Closed_Cum_Est = Closed_Cum_Est + Closed_Bugs_Est
         sprintData['Closed_Cum_Table'].append(round(Closed_Cum_Est))
         sprintData['Closed_Cum_Est'].append(round(Closed_Cum_Est))


         # Diff (Created - Resolved)
         Diff_Est = Created_Bugs_Est - Resolved_Bugs_Est
         sprintData['Diff_Est'].append(round(Diff_Est))      
         sprintData['Diff_Table'].append(round(Diff_Est))

         Open_Est = Open_Est + Diff_Est
         sprintData['Open_Est'].append(round(Open_Est))
         sprintData['Open_Table'].append(round(Open_Est))
      

# Main Code

with open('config.json') as config_file:
    configData = json.load(config_file)

# Get Day of Begin and Day of End in Each Sprint
# getstartEndDate() returns dictionary

sprints = getStartEndDate(configData['startDay'], configData['first_sprint'], configData['final_sprint'], configData['sprint_length'])
weeks = getStartEndDate(configData['startDay'], configData['first_week'], configData['final_week'], configData['week_length'])

# Calculate the expected number of New Bug per sprint based on past 5 sprints
#Created_Bugs_Est_from_start = estimateFutureBugCount(configData['first_sprint'], sprints)

Created_Bugs_Est = round(estimateFutureBugCount(configData['current_sprint'], sprints, configData)/2)
print("Predicted Future Bug Count Base: " + str(Created_Bugs_Est))

BugResolvedDaily = round(estimateDailyBugFixCount(configData['current_sprint'], configData, sprints, p1_pri, 'Resolved', 'UI'), 2)
print("Predicted Bug Resolved per man day: " + str(BugResolvedDaily))

BugClosedDaily = round(estimateDailyBugFixCount(configData['current_sprint'], configData, sprints, p1_pri, 'Closed', 'QA'), 2)
print("Predicted Bug Closed per man day: " + str(BugClosedDaily))

query = composeQuery(sprints[configData['first_sprint']]['start'], sprints[configData['first_sprint']]['end'], 'Open', 'Bug, Defect', p1_pri)
totalOpen = getIssueTotal(query, configData)
print("Open Bugs at initial point of this report: " + str(totalOpen))

# Generate Sprint Data Dictionary
collectData(sprintData, 
            weeks, 
            Created_Bugs_Est, 
            BugResolvedDaily, 
            BugClosedDaily, 
            totalOpen, 
            configData, 
            configData['milestone_week'], 
            configData['current_week'])

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=False,
    vertical_spacing=0.03,
    subplot_titles=("main", "Accumulated Graph", "Data"),
    specs=[[{"secondary_y": True}],
           [{"secondary_y": False}],
           [{"type": "table"}]]
)


fig.add_trace(addBarToList('Created', '#F74F4F', 1.0), row=1, col=1, secondary_y=False)
fig.add_trace(addBarToList('Created_Est', '#F74F4F', 0.4), row=1, col=1, secondary_y=False)

fig.add_trace(addBarToList('Resolved', 'green', 1.0), row=1, col=1, secondary_y=False)
fig.add_trace(addBarToList('Resolved_Est', 'green', 0.4), row=1, col=1, secondary_y=False)

fig.add_trace(addBarToList('Closed', 'blue', 1.0), row=1, col=1, secondary_y=False)
fig.add_trace(addBarToList('Closed_Est', 'blue', 0.4), row=1, col=1, secondary_y=False)

fig.add_trace(addBarToList('Diff', 'grey', 1.0), row=1, col=1, secondary_y=False)
fig.add_trace(addBarToList('Diff_Est', 'grey', 0.5), row=1, col=1, secondary_y=False)

#fig.add_trace(addScatterToList('Created', '#F74F4F', 'lines+markers', 'solid', 'Created', 'circle'), row=1, col=1, secondary_y=False)
#fig.add_trace(addScatterToList('Created_Est', '#F74F4F', 'lines+markers', 'dot', 'Created Forecast', 'circle'), row=1, col=1, secondary_y=False)

#fig.add_trace(addScatterToList('Resolved', 'green', 'lines+markers', 'solid', 'Resolved', 'circle'), row=1, col=1, secondary_y=False)
#fig.add_trace(addScatterToList('Resolved_Est', 'green', 'lines+markers', 'dot', 'Resolved Forecast', 'circle'), row=1, col=1, secondary_y=False)

#fig.add_trace(addScatterToList('Closed', 'blue', 'lines+markers', 'solid', 'Closed', 'circle'), row=1, col=1, secondary_y=False)
#fig.add_trace(addScatterToList('Closed_Est', 'blue', 'lines+markers', 'dot', 'Closed Forecast', 'circle'), row=1, col=1, secondary_y=False)

fig.add_trace(addScatterToList('Open_Est', '#F1CC70', 'lines+markers', 'dot', 'Open Forecast', 'square'), row=1, col=1, secondary_y=False)
fig.add_trace(addScatterToList('Open', '#F1CC70', 'lines+markers', 'solid', 'Open', 'square'), row=1, col=1, secondary_y=False)

#fig.add_trace(addScatterToList('Diff', 'grey', 'lines+markers', 'solid', 'Diff (Created - Resolved)', 'circle'), row=1, col=1, secondary_y=False)
#fig.add_trace(addScatterToList('Diff_Est', 'grey', 'lines+markers', 'dot', 'Diff (Created - Resolved) - Forecast', 'circle'), row=1, col=1, secondary_y=False)

fig.add_trace(addScatterToList('Created_Cum', '#F74F4F', 'lines+markers+text', 'solid', 'Created Sum', 'circle'), row=2, col=1, secondary_y=False)
fig.add_trace(addScatterToList('Created_Cum_Est', '#F74F4F', 'lines+markers+text', 'dot', 'Created Sum Forecast', 'circle'), row=2, col=1, secondary_y=False)
fig.add_trace(addScatterToList('Resolved_Cum', 'green', 'lines+markers', 'solid', 'Resolved Sum', 'circle'), row=2, col=1, secondary_y=False)
fig.add_trace(addScatterToList('Resolved_Cum_Est', 'green', 'lines+markers', 'dot', 'Resolved Sum Forecast', 'circle'), row=2, col=1, secondary_y=False)
fig.add_trace(addScatterToList('Closed_Cum', 'blue', 'lines+markers', 'solid', 'Closed Sum', 'circle'), row=2, col=1, secondary_y=False)
fig.add_trace(addScatterToList('Closed_Cum_Est', 'blue', 'lines+markers', 'dot', 'Closed Sum Forecast', 'circle'), row=2, col=1, secondary_y=False)

#fig.add_trace(addScatterToList('Open_Est_Future', '#F74F4F', 'lines+markers', 'dot', 'Open Forecast'), row=1, col=1, secondary_y=True)


headerList = ['Sprint', 'Open', 'Created', 'Resolved', 'Closed', 'Diff (Created - Resolved)', 'Created Cum', 'Resolved Cum', 'Closed_Cum']

#font_color = ['rgb(40,40,40)', ['rgb(255,0,0)' if int(v) > curSprint else 'rgb(10,10,10)' for v in sprintData['Sprints']]]

fig.add_trace(go.Table(
    header=dict(values=headerList,
                line_color='darkslategray',
                fill_color='lightskyblue',
                align='center'),
    cells=dict(values=[sprintData['Sprints'], # 1st column
                       sprintData['Open_Table'],
                       sprintData['Created_Table'],
                       sprintData['Resolved_Table'],
                       sprintData['Closed_Table'],
                       sprintData['Diff_Table'],
                       sprintData['Created_Cum_Table'],
                       sprintData['Resolved_Cum_Table'],
                       sprintData['Closed_Cum_Table'],
                       ], 
               line_color='darkslategray',
               fill_color='lightcyan',
#               font = dict(color=font_color),
               align='center')), row=3, col=1)


fig.update_layout(
    height=2000,
    showlegend=True,
    title_text="Bug Forecast",
    barmode='group'
)

fig.update_xaxes(
   dtick=604800000, 
   tick0='2020-01-01',
   tickfont=dict(size=10),
   showline=True,
   zeroline=True,
   showgrid=True,
   mirror=True,
)

fig.update_yaxes(
   title_text="<b>Created and Resolved</b>",
   secondary_y=False,
   range=[-200, 2500],
   dtick=100,                
   gridcolor='#DDD',
   row=1, col=1,
)

fig.update_yaxes(
   title_text="<b>Accumulated total</b>", 
   range=[0, 5000], 
   dtick=500,                
   gridcolor='#DDD',
   row=2, col=1,
)

fig.update_yaxes(
   title_text="<b>Open Tickets</b>", 
   secondary_y=True
)

#fig.layout.yaxis.update({'range': [-500, 1000]})
#fig.layout.yaxis.update({'dtick': 100})
#fig.layout.xaxis.update({'dtick': 1})

#fig.layout.xaxis.update({'tick0': 19})


fig.show()

plotly.offline.plot(fig, filename = 'SprintReport.html', auto_open=False)


