# Import smtplib for the actual sending function
import sys
sys.path.append("Modules")
import stock, weather

# Import the email modules
import smtplib, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email Information
you = "yoheisakata@hotmail.com"
me = "yoheisakata80@gmail.com"

# Gmail Credential
gmail_user = "yoheisakata80@gmail.com"
gmail_pwd = "yosemiteGG4"

# Stock Information
# Stock Name, Volume, Target Price
stocks = [["FB", 1230, 120, 25.22], ['TWTR', 371, 70, 35.82], ['AAPL', 430, 150, 91.76] ]

def printStockData(each_stock, qty, tar_price, pur_price):	
	tinker = each_stock[0]
	cur_price = each_stock[2]
	pur_val = str(int(float(pur_price)*qty))
	cur_val = str(int(float(cur_price)*qty))
	tar_val = str(int(tar_price*qty))
	cur_rev = str(int(stock.getRevenue(tinker, pur_price, qty)*0.85))
	tar_rev = str(int(stock.getRevenueTarget(tar_price, pur_price, qty)*0.85))
	dollar_change = each_stock[3]
	percent_change = each_stock[4]
	output="<tr align=\"center\"><td>%s</td><td>$%s</td><td>$%s</td><td>$%s</td><td>$%s</td><td>$%s</td><td>$%s</td><td>$%s</td><td>$%s</td><td>$%s</td><td>%s</td></tr>" % (tinker, pur_price, cur_price, pur_val, cur_val, cur_rev, tar_price, tar_val, tar_rev, dollar_change, percent_change)	
	return output

def printWeatherData(weather):
	message="<h3>%s %s %s %s %s</h3>" % (weather['state'], weather['city'], weather['localtime'], weather['current_temp_f'], weather['current_temp_c'])
	return message

msg = MIMEMultipart('alternative')
msg['Subject'] = "Stock Report: " + str(time.strftime("%x"))
msg['From'] = me
msg['To'] = you


text = """\
From: Yohei <yoheisakata80@gmail.com>
To: Yohei <yoheisakata80@gmail.com>
MIME-Version: 1.0
Content-type: text/html
Subject: Morning Report

Simple Text
"""


stockSection = """
<table border=\"1\" style=\"width:800px\">
<tr>
	<th>Stock</th>
	<th>Purchased Price</th>
	<th>Current Price</th>
	<th>Cost Spent</th>
	<th>Current Value</th>
	<th>Current Revenue</th>
	<th>Target Price</th>
	<th>Target Value</th>
	<th>Target Revenue</th>
	<th>Dollar</th>
	<th>Percent</th>
</tr>"""

for each in stocks:
	stockSection += printStockData(stock.getStockData(each[0]), each[1], each[2], each[3])

stockSection +=  "<tr align=\"center\"><td>Total</td><td></td><td></td>" \
+ "<td>$" + str(int(stock.getTotalSpent(stocks))) + "</td>" \
+ "<td>$" + str(int(stock.getTotalCurrent(stocks))) + "</td>" \
+ "<td>$" + str(int(stock.getTotalRevenueCurrent(stocks)*0.85)) + "</td>" \
+ "<td></td>" \
+ "<td>$" + str(int(stock.getTotalTarget(stocks))) + "</td>" \
+ "<td>$" + str(int(stock.getTotalRevenueTarget(stocks)*0.85)) + "</td>" \
+ "</tr>" + "</table>"

#weatherSection = printWeatherData(weather.getWeatherData('Seattle', 'WA'))


html = """\
<html>
  <head></head>
  <body>
""" + "<h1> Morning Report </h1>" + """\
""" + "<h2>" + time.strftime("%Y/%m/%d") + "</h2>" + """\
""" + stockSection + """\
  </body>
</html>
"""

#print html

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)


#try:
smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.login(gmail_user, gmail_pwd)
smtpObj.sendmail(me, you, msg.as_string())         
#smtpObj.sendmail(me, you, message)         
print "Successfully sent email"
#except SMTPException:
#   print "Error: unable to send email"
#
#smtpObj.quit()