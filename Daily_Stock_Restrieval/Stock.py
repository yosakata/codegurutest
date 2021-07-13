import httplib
import csv
import urllib2
import StringIO
# Import the email modules
import smtplib, time

def getStockData(tinker):
	"""
	:param str tinker: stock name
	:rtype: list
	:return: stock data (e.g. ['AAPL', 'Apple Inc.', '125.81', '+1.28', '+1.03%'])
	"""	
	url = 'http://download.finance.yahoo.com/d/quotes.csv?s='+tinker+'&f=snl1c1p2&e=.csv'
	cr = csv.reader(urllib2.urlopen(url))
	for rows in cr:
		return rows

def getStockPrice(tinker):
	stockData = getStockData(tinker)
	return stockData[2]

def getStockValue(tinker, qty):
	stockData = getStockData(tinker)
	return float(StockData[2]) * qty

def getCurrentRevenue(tinker, purchasedPrice, qty):
	return int((float(getStockPrice(tinker)) - float(purchasedPrice)) * qty * 0.85)

def getTargetRevenue(tar_price, purchasedPrice, qty):
	return int((float(tar_price) - float(purchasedPrice)) * qty	* 0.85)

def getTotalCurrentValue(stocks):
	total = 0
	for stock in stocks:
		tinker = stock[0]
		currentPrice = float(getStockPrice(tinker))
		qty = stock[1]
		total += (currentPrice * qty)
	return int(total)

def getTotalCost(stocks):
	total = 0
	for stock in stocks:
		purchasedPrice = float(stock[2])
		qty = stock[1]
		total += (purchasedPrice * qty)
	return int(total)

def getTotalTargetValue(stocks):
	total = 0
	for stock in stocks:
		targetPrice = float(stock[3])
		qty = stock[1]
		total += (targetPrice * qty)
	return int(total)

def getTotalTargetRevenue(stocks):
	return float(getTotalTargetValue(stocks) - getTotalCost(stocks)) * 0.85

def getTotalCurrentRevenue(stocks):
	return float(getTotalCurrentValue(stocks) - getTotalCost(stocks)) * 0.85

def getTableHeader():
	tableHeader = """
	<table border=\"1\" style=\"width:1000px\">
	<tr>
	<th></th>
	<th colspan="3">Purchased</th>
	<th colspan="3">Current</th>
	<th colspan="3">Target</th>
	</tr>
	<tr>
		<th>Stock</th>
		<th>Price</th>
		<th>Quantity</th>
		<th>Cost</th>
		<th>Price</th>
		<th>Value</th>
		<th>Revenue</th>
		<th>Price</th>
		<th>Value</th>
		<th>Revenue</th>
	</tr>"""
	return tableHeader

def getStockSummary(tinker, qty, purchasedPrice, targetPrice):
	currentPrice          = getStockPrice(tinker)
	cost                       = int(float(purchasedPrice)*qty)
	currentValue          = int(float(currentPrice)*qty)
	targetValue            = int(float(targetPrice)*qty)
	currentRevenue     = int(getCurrentRevenue(tinker, purchasedPrice, qty))
	targetRevenue       = int(getTargetRevenue(targetPrice, purchasedPrice, qty))

	stockSummary = "<tr align=\"center\">" \
	+ "<td>" + tinker + "</td>" \
	+ "<td>$" + str(purchasedPrice) + "</td>" \
	+ "<td>"   + str(qty) + "</td>" \
	+ "<td>$" + str(cost) + "</td>" \
	+ "<td>$" + str(currentPrice) + "</td>" \
	+ "<td>$" + str(currentValue) + "</td>" \
	+ "<td>$" + str(checkRevenue(currentRevenue)) + "</td>" \
	+ "<td>$" + str(targetPrice) + "</td>" \
	+ "<td>$" + str(targetValue) + "</td>"	\
	+ "<td>$" + str(targetRevenue) + "</td>"	\
	+ "</tr>"
	return stockSummary

def checkRevenue(price):
	if price < 0:
		return "<font color=\"red\">" + str(price) + "</font>"
	else:
		return price

def getStockTotalSummary(stocks):
	stockTotalSummary =  "<tr align=\"center\"><td>Total</td>" \
	+ "<td></td><td></td>" \
	+ "<td>$" + str(int(getTotalCost(stocks))) + "</td>" \
	+ "<td></td>" \
	+ "<td>$" + str(getTotalCurrentValue(stocks)) + "</td>" \
	+ "<td>$" + str(getTotalCurrentRevenue(stocks)) + "</td>" \
	+ "<td></td>" \
	+ "<td>$" + str(getTotalTargetValue(stocks)) + "</td>" \
	+ "<td>$" + str(getTotalTargetRevenue(stocks)) + "</td>" \
	+ "</tr>"
	return stockTotalSummary

def getSummaryTable(stocks):
	summaryTable = getTableHeader()
	for stock in stocks:
		tinker                 = stock[0]
		qty                     = stock[1]
		purchasedPrice  = stock[2]
		targetPrice         = stock[3]
		summaryTable   += getStockSummary(tinker, qty, purchasedPrice, targetPrice)
	summaryTable += getStockTotalSummary(stocks)
	summaryTable += "</table>"		
	return summaryTable

if __name__ == '__main__':
	# Stock Name, Volume, Purchased Price, Target Price
	stocks = [['AAPL', 407, 91.76, 150], ['BABA', 310, 86.80, 100], ["FB", 1230, 25.22, 130], ['TWTR', 371, 35.82, 70]]

	print "<html>"
	print "<head><title>Stock Summary on " + time.strftime("%Y/%m/%d") + "</title></head>"
	print "<body>"
	print getSummaryTable(stocks)	
	print "</body>"
	print "</html>"

