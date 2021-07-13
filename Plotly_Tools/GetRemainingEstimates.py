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

fixVersion = "SW10"
startAt = 0
maxResult = 1
sprintTable = [['Sprint', 'Crated', 'Created Cum', 'Resolved', 'Resolved Cum', 'Open']]
sprintDataDict = {'Sprints': [], 'Created': [], 'Created_Cum': [], 'Resolved': [], 'Resolved_Cum': [], 'Open': []}
start_sprint = 19
end_sprint = 30
created_cum = 0
resolved_cum = 0
p1_pri = 'Blocker, "A(1) - Critical", "B(2) - High"'
sprints = {}

daysList = ['2020-02-01', '2020-02-02', '2020-02-03', '2020-02-04', '2020-02-05', '2020-02-06' ]
storyListTime = [200, 200, 150, 120, 100]
storyListLogged = [20, 40, 80, 90, 120 ]
storyForecast = [200, 180, 150, 100, 50, 0]



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

def getTotalOfIssus(query, startAt, maxResult):
   results = getResultsFromJIRA(query, startAt, maxResult)
   return int(results["total"])

def drawPlot(sprintList, sprint_created, sprint_created_cum, sprint_resolved, sprint_resolved_cum, sprint_open):
   fig = go.Figure()
   
   fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    specs=[[{"type": "scatter"}],
           [{"type": "scatter"}],
           [{"type": "scatter"}]]
   )
   fig.add_trace(go.Scatter(x=sprintList, y=sprint_created, mode="lines", line=dict(color='royalblue', width=5, dash='dot')), row=3, col=1)
   fig.add_trace(go.Scatter(x=sprintList, y=sprint_created_cum, mode="lines", name="mining revenue"), row=3, col=1)
   fig.add_trace(go.Scatter(x=sprintList, y=sprint_created, mode="lines", name="mining revenue"), row=1, col=1)
   fig.update_layout(height=800, showlegend=False, title_text="Bitcoin mining stats for 180 days",)



   #fig.add_trace(go.Scatter(x=sprintList, y=sprint_created, name='Created',line=dict(color='royalblue', width=5, dash='dot')))
   #fig.add_trace(go.Scatter(x=sprintList, y=sprint_created_cum, name='Created Cum',line = dict(color='firebrick', width=5, dash='dot')))
   #fig.add_trace(go.Scatter(x=sprintList, y=sprint_resolved, name='Resolved',line=dict(color='blue', width=5, dash='dot')))
   #fig.add_trace(go.Scatter(x=sprintList, y=sprint_resolved_cum, name='Resolved Cum',line = dict(color='red', width=5, dash='dot')))
   #fig.add_trace(go.Scatter(x=sprintList, y=sprint_open, name='Open Issues',line = dict(color='black', width=5, dash='dot')))

   # Edit the layout
   #fig.update_layout(title='Burndown Chart', xaxis_title='Sprint',yaxis_title='Total')
   fig.show()
   #fig.write_image("chart.jpg")

def getSprintDays(year, month, day, startSprint, endSprint, sprintTable):
   sprintDict = {}
   sprint = startSprint
   start_date = date(year, month, day)
   while True:
      if sprint > endSprint:
         break
      end_date = start_date + timedelta(days=13)
      sprintDict[sprint] = {'DayOfBegin': str(start_date), 'DayOfEnd': str(end_date)}
      start_date = start_date + timedelta(days=14)
      sprint = sprint + 1
   return sprintDict


dailyList = []

def generateDailyRange(startDay, endDay, dailyList):
   dayNum = 1
   while True:
      d = datetime.fromisoformat(startDay) + timedelta(days=dayNum)
      #print(datetime.date(d))
      curDay = d
      dailyList.append(str(datetime.date(d)))
      if datetime.date(curDay) >  datetime.date(datetime.fromisoformat(endDay)):
         break
      dayNum = dayNum + 1


generateDailyRange('2020-02-01', '2020-02-08', dailyList)

dailyDict = {'daily': [], 'In Progress': [], 'Open': [], 'Resolved': [], 'Blocked': [], 'TotalOpen': []}

'''
for daily in dailyList:
   # Add day to daily list
   dailyDict['daily'].append(daily)

   # Add Total of Open issues to Open List on that day
   query = 'type in (defect, bug) and status was "Open" on ' + daily
   total = getTotalOfIssus(query, startAt, maxResult)
   dailyDict['Open'].append(total)

   # Add Total of Issues that are resolved on the day
   query = 'type in (defect, bug) and status was "In Progress" on ' + daily
   total = getTotalOfIssus(query, startAt, maxResult)
   dailyDict['In Progress'].append(total)

   # Add Total of Issues that are resolved on the day
   query = 'type in (defect, bug) and status was "Blocked" on ' + daily
   total = getTotalOfIssus(query, startAt, maxResult)
   dailyDict['Blocked'].append(total)

   query = 'type in (defect, bug) and status was not in (Resolved, closed) on ' + daily
   total = getTotalOfIssus(query, startAt, maxResult)
   dailyDict['TotalOpen'].append(total)


   query = 'type in (defect, bug) and status was "Resolved" on ' + daily
   total = getTotalOfIssus(query, startAt, maxResult)
   dailyDict['Resolved'].append(total*-1)

'''

dailyDict = {'daily': ['2020-02-02', '2020-02-03', '2020-02-04', '2020-02-05', '2020-02-06', '2020-02-07', '2020-02-08', '2020-02-09'], 'In Progress': [14, 25, 23, 29, 29, 28, 17, 15], 'Open': [166, 187, 195, 186, 199, 181, 169, 177], 'Resolved': [-187, -216, -213, -203, -223, -212, -197, -195], 'Blocked': [7, 9, 8, 10, 11, 13, 12, 14], 'TotalOpen': [471, 440, 426, 415, 384, 363, 358, 351]}

#print(dailyDict)

#dailyDict = {'daily': ['2020-01-02', '2020-01-03', '2020-01-04', '2020-01-05', '2020-01-06', '2020-01-07', '2020-01-08', '2020-01-09', '2020-01-10', '2020-01-11', '2020-01-12', '2020-01-13', '2020-01-14', '2020-01-15', '2020-01-16', '2020-01-17', '2020-01-18', '2020-01-19', '2020-01-20', '2020-01-21', '2020-01-22', '2020-01-23', '2020-01-24', '2020-01-25', '2020-01-26', '2020-01-27', '2020-01-28', '2020-01-29', '2020-01-30', '2020-01-31'], 'In Progress': [14, 17, 12, 15, 20, 23, 21, 25, 39, 13, 21, 38, 32, 36, 30, 31, 24, 24, 29, 32, 26, 23, 19, 15, 15, 25, 29, 29, 36, 22], 'Open': [151, 149, 142, 145, 180, 187, 199, 208, 219, 200, 203, 215, 213, 217, 223, 215, 203, 200, 200, 207, 196, 189, 198, 189, 188, 203, 192, 189, 191, 176], 'Resolved': [-139, -136, -134, -134, -140, -148, -164, -169, -181, -170, -172, -206, -200, -195, -160, -146, -113, -112, -119, -136, -133, -136, -141, -138, -139, -151, -160, -172, -194, -194]}

#print(dailyDict)

sprints = getSprintDays(2019, 10, 9, start_sprint, end_sprint, sprintTable)

'''
for sprint in sprints:
   sprintDataDict['Sprints'].append(sprint)
   tmpList = [sprint]

   # Created
   query = composeQuery(sprints[sprint]['DayOfBegin'], sprints[sprint]['DayOfEnd'], 'Created', p1_pri)
   total = getTotalOfIssus(query, startAt, maxResult)
   sprintDataDict['Created'].append(total)
   tmpList.append(total)

   # Created Accumulated 
   created_cum = created_cum + total
   sprintDataDict['Created_Cum'].append(created_cum)
   tmpList.append(created_cum)

   # Resolved   
   query = composeQuery(sprints[sprint]['DayOfBegin'], sprints[sprint]['DayOfEnd'], 'Resolved', p1_pri)
   total = getTotalOfIssus(query, startAt, maxResult)
   sprintDataDict['Resolved'].append(total)
   tmpList.append(total)


   # Resolved Accumulated
   resolved_cum = resolved_cum + total
   sprintDataDict['Resolved_Cum'].append(resolved_cum)
   tmpList.append(resolved_cum)

   # Open 
   query = composeQuery(sprints[sprint]['DayOfBegin'], sprints[sprint]['DayOfEnd'], 'Open', p1_pri)
   total = getTotalOfIssus(query, startAt, maxResult)
   sprintDataDict['Open'].append(total)
   tmpList.append(total)


   # Add Data to each sprint row
   sprintTable.append(tmpList)
'''

sprintTable = [['Sprint', 'Created', 'Created Cum', 'Resolved', 'Resolved Cum', 'Open'], [19, 60, 60, 60, 60, 1093], [20, 37, 97, 63, 123, 1042], [21, 94, 191, 105, 228, 949], [22, 51, 242, 63, 291, 902], [23, 173, 415, 150, 441, 769], [24, 37, 452, 95, 536, 690], [25, 137, 589, 155, 691, 546], [26, 76, 665, 130, 821, 444], [27, 168, 833, 217, 1038, 256], [28, 74, 907, 51, 1089, 221], [29, 0, 907, 0, 1089, 232], [30, 0, 907, 0, 1089, 232]]


sprintDataDict = {'Sprints': [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30], 'Created': [60, 37, 94, 51, 173, 37, 137, 76, 168, 74, 0, 0], 'Created_Cum': [60, 97, 191, 242, 415, 452, 589, 665, 833, 907, 907, 907], 'Resolved': [60, 63, 105, 63, 150, 95, 155, 130, 217, 51, 0, 0], 'Resolved_Cum': [60, 123, 228, 291, 441, 536, 691, 821, 1038, 1089, 1089, 1089], 'Open': [1093, 1042, 949, 902, 769, 690, 546, 444, 256, 221, 232, 232]}





fig = ff.create_table(sprintTable, height_constant=50)

trace1 = go.Scatter(x=sprintDataDict['Sprints'], y=sprintDataDict['Created'],
                    marker=dict(color='#0099ff'),
                    mode="lines+markers+text",
                    name='Created',
                    xaxis='x2', 
                    yaxis='y2',
                    text=sprintDataDict['Created'],
                    textposition="bottom center"
                    )
trace2 = go.Scatter(x=sprintDataDict['Sprints'], y=sprintDataDict['Resolved'],
                    mode="lines+markers+text",
                    marker=dict(color='#4040FF'),
                    name='Resolved',
                    xaxis='x2',
                    yaxis='y2',
                    text=sprintDataDict['Resolved'],
                    textposition="top center"
                    )

trace3 = go.Scatter(x=sprintDataDict['Sprints'], y=sprintDataDict['Open'],
                    marker=dict(color='#114040'),
                    mode="lines+markers+text",
                    name='Open',
                    xaxis='x2',
                    yaxis='y2',
                    text=sprintDataDict['Open'],
                    textposition="top right"
                    )
trace4 = go.Bar(x=sprintDataDict['Sprints'], y=sprintDataDict['Resolved'], xaxis='x2', yaxis='y2',
                marker=dict(color='#0099ff'),
                text=sprintDataDict['Resolved'],
                textposition='auto',
                name='Resolved')


trace5 = go.Bar(x=sprintDataDict['Sprints'], y=sprintDataDict['Created'], xaxis='x2', yaxis='y2',
                marker=dict(color='#ffBBff'),
                text=sprintDataDict['Created'],
                textposition='auto',
                name='Created')

traceA = go.Bar(x=dailyDict['daily'], y=dailyDict['Open'], xaxis='x2', yaxis='y2',
                marker=dict(color='#FFB833'),
                text=dailyDict['Open'],
                textposition='auto',
                name='Open')

traceB = go.Bar(x=dailyDict['daily'], y=dailyDict['In Progress'], xaxis='x2', yaxis='y2',
                marker=dict(color='#DAF7A6'),
                text=dailyDict['In Progress'],
                textposition='auto',
                name='In Progress')

traceC = go.Bar(x=dailyDict['daily'], y=dailyDict['Resolved'], xaxis='x2', yaxis='y2',
                marker=dict(color='#C70039'),
                text=dailyDict['Resolved'],
                textposition='auto',
                name='Resolved')


traceD = go.Bar(x=dailyDict['daily'], y=dailyDict['Blocked'], xaxis='x2', yaxis='y2',
                marker=dict(color='#432E07'),
                text=dailyDict['Blocked'],
                textposition='auto',
                name='Blocked')


traceE = go.Scatter(x=dailyDict['daily'], y=dailyDict['TotalOpen'],
                    marker=dict(color='#0099ff'),
                    mode="lines+markers+text",
                    name='TotalOpen',
                    xaxis='x2', 
                    yaxis='y2',
                    text=dailyDict['TotalOpen'],
                    textposition="bottom center"
                    )



fig.update_layout(barmode='relative')

fig.add_traces([traceA, traceB, traceC, traceD])


#fig.add_traces([trace3, trace4, trace5])

# initialize xaxis2 and yaxis2
fig['layout']['xaxis2'] = {}
fig['layout']['yaxis2'] = {}

# Edit layout for subplots
fig.layout.xaxis.update({'domain': [0, 0.5]})
fig.layout.xaxis2.update({'domain': [0.6, 1.]})
fig.layout.xaxis.update({'title': 'Sprints'})
fig.layout.xaxis2.update({'title': 'Sprints'})

# The graph's yaxis MUST BE anchored to the graph's xaxis
fig.layout.yaxis2.update({'anchor': 'x2'})
fig.layout.yaxis2.update({'title': 'Issues'})

# Update the margins to add a title and see graph x-labels.
fig.layout.margin.update({'t':50, 'b':50})
fig.layout.update({'title': 'Sprint Analysis'})

fig.update_yaxes(tick0=-50, dtick=10)
#fig.update_xaxes(tick0=19, dtick=1)


plotly.offline.plot(fig, filename = 'filename.html', auto_open=False)

#fig.show()


