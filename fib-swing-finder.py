#!/usr/bin/env python3
import csv

#This script examines daily stock data and searches for instances of swings that result in a bounce and a new high
#within certain criteria. It examines wheter or not the bounce occurred on a fibonacci retracement level.
#The output is a series of data points that include:
#The swin startd date, the swing end date, the swing's low, the swing's high, the price at which it bounced
#and the peak price it obtained after a recovery

#get the data from Alpha Vantage using this URL:
#https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&apikey={Your API key here}&datatype=csv&outputsize=full&symbol={symbol}

#Open the resulting CSV in a spreadsheet program, sort it by date and add a 10 day moving average column

data_array = []
with open('{path to CSV file}.csv', newline='') as csvfile:
    contents = csv.reader(csvfile, delimiter=',')
    for row in contents:
        data_array.append(row)

debug = 0

consecutiveAboveMA = 0
consecutiveBelowMA = 0
swingStartDate = 0
swingStartPosition = 0
swingEndDate = 0
swingEndPosition = 0
swingHigh = 0
swingLow = 0
trendBegun = 0
trendBroken = 0
recoveryBegun = 0
recoveryValid = 0
recoveryBroken = 0
recoveryOver = 0

position = 0
while position < len(data_array):
    i = data_array[position]
    if debug == 1:
        if position > 540:
            break
    #headers are
    #timestamp,open,high,low,close,volume,10 sma
    #First rows will be missing data for the moving average columns, so we skip those
    if position < 11:
        position += 1
        continue
    #pick the data out
    date = i[0]
    low = i[3]
    high = i[2]
    close =i[4]
    MA = i[6]
    #See if the close is above or below the MA
    if close >= MA:
        consecutiveAboveMA += 1
        consecutiveBelowMA = 0
    elif close < MA:
        consecutiveBelowMA += 1
        consecutiveAboveMA = 0
    else:
        print("Couldn't determine whether closed above or below the MA.")
    if (consecutiveAboveMA > 9 and trendBegun == 0 and recoveryBegun == 0):
        if debug == 1:
            print("Trend begun on "+data_array[position-9][0])
        #this may be the start of a swing
        trendBegun = 1
        swingStartPosition = position-9
        swingStartDate = data_array[swingStartPosition][0]
        swingLow = data_array[swingStartPosition][3]
    if consecutiveBelowMA > 4 and trendBegun == 1:
        if debug == 1:
            print("trend broken on "+i[0])
        trendBroken = 1
    if trendBegun == 1 and trendBroken == 1 and recoveryBegun == 0:
        #We have concluded a swing
        swingEndPosition = position-4
        swingEndDate = data_array[swingEndPosition][0]
        #go through all the highs of the swing to find the actual high
        swingHighs = []
        for row in data_array[swingStartPosition:swingEndPosition]:
            swingHighs.append(row[2])
        swingHigh = max(swingHighs)
        swingHighs = None
        trendBroken = 0
        trendBegun = 0
        recoveryBegun = 1
        if debug == 1:
            print("swing over on "+i[0]+", checking recovery...")
    #Recovery is only valid if price > swing high within xx candles
    if recoveryBegun == 1:
        if close > swingHigh:
            if debug == 1:
                print("***Recovery valid above swing high on"+i[0])
            recoveryValid = 1
            #Find the bounce
            #Go through lows between SwingHigh and Recover to find lowest = bounce
            recoveryLows = []
            for low in data_array[swingEndPosition:position]:
                recoveryLows.append(low[3])
            bouncePrice = min(recoveryLows)
            recoveryLows = None
        if position > swingEndPosition+30 and recoveryValid != 1:
            if debug == 1:
                print("Recovery broken on "+i[0])
            recoveryBroken = 1
    if recoveryBroken == 1:
        #recovery failed, clear everything and start over
        if debug == 1:
            print("Swing failed, starting over...")
        swing = []
        swingHigh = None
        swingLow = None
        swingStartDate = None
        swingEndDate = None
        recoveryBegun = 0
        recoveryBroken = 0
        recoveryValid = 0
        trendBegun = 0
        trendBroken = 0
        consecutiveAboveMA = 0
        consecutiveBelowMA = 0
        #instead of advancing one position and continuing, go back to
        #10 days after the start of this swing, in case we missed the 
        #start of a new swing
        position = swingStartPosition +10
        if debug == 1:
            print("position = "+str(position))
        swingStartPosition = None
        continue
    if recoveryValid == 1 and recoveryOver == 0 and consecutiveBelowMA > 4:
        if debug == 1:
            print("Recovery is over at "+i[0]+" - position "+str(position))
        #Find the peak recovery price
        #Go through the highs between the SH and recovery to find highest high
        recoveryHighs = []
        for high in data_array[swingEndPosition:position]:
            recoveryHighs.append(high[2])
        peakPrice = max(recoveryHighs)
        if debug == 1:
            print("Recovery over on "+i[0]+" with peak price of "+peakPrice)
        recoveryOver = 1
    if recoveryValid == 1 and recoveryOver == 1:
        if debug == 1:
            print("swing started on "+swingStartDate+" (position "+str(swingStartPosition)+") with a low of $"+swingLow)
            print("     swing ended on "+swingEndDate+" (position "+str(swingEndPosition)+") with a high of $"+swingHigh)
            print("     Bounce price was $"+bouncePrice)
            print("     Peak price was $"+peakPrice)
        print(swingStartDate+','+swingEndDate+','+swingLow+','+swingHigh+','+bouncePrice+','+peakPrice)
        #This, ladies & gentlemen is the end of the show
        swing = []
        swingHigh = None
        swingLow = None
        swingStartDate = None
        swingEndDate = None
        swinStartPosition = None
        recoveryBegun = 0
        recoveryBroken = 0
        recoveryValid = 0
        recoveryOver = 0
        trendBegun = 0
        trendBroken = 0
        consecutiveAboveMA = 0
        consecutiveBelowMA = 0
        peakPrice =None
        bouncePrice = None
    position += 1

