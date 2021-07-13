if [ ! -d "./Stocks" ]; then
	mkdir ./Stocks
fi
curTime=`date +%y%m%d_%H%M`
python ./Stock.py > ./Stocks/${curTime}_StockReport.html
