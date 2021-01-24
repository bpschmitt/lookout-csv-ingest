
import time
import random
from datetime import datetime, timedelta

sensitivity = 50

timeStamp = datetime.now()


apps = [ "demobrad-STB-guideService", "demobrad-STB-purchase", "demobrad-STB-otaUpdates", "demobrad-STB-streaming", "demobrad-billing-paymentGateway", "demobrad-billing-portal", "demobrad-CSA-portal", "demobrad-CSA-webSelfServ", "demobrad-PROV-STB", "demobrad-SAMLgateway", "demobrad-Android-streaming" ]
appCounts = [ 500, 25, 10, 1000, 100, 25, 100, 750, 10, 25, 100 ]

appToFail = "demobrad-SAMLgateway"
appImpactRegex = "CSA"


for chunks in range(1):
    fName = "chunk-" + timeStamp.strftime( "%m%d%y-%H" )
    print("generating data for time window " + fName)
    f = open( fName, "w" )
    s = "timeStamp,appName,hostName,cpu_idle,mem_util,txnCount,errCount\n"
    f.write( s )

    print( "writing 3600 seconds of data for cluster" )
    chaosMode = False
    wasChaotic = False
    minTimeInChaos = 15 * 60
    chaosStartTime = 0

    for timeRangeInSecs in range(60):
        if( chaosMode == False and wasChaotic == False ):
            chaos = random.randrange( 100 )
            if( chaos > sensitivity ):
                print("IN CHAOS MODE NOW FOR: " + appToFail + " " +  timeStamp.strftime( "%s" ))
                chaosMode = True
                wasChaotic = True
                chaosStartTime = timeStamp.strftime( "%s" )
    
        i = 0
        epochTime = timeStamp.strftime( "%s" )
    
        if( chaosMode == True and int(epochTime) - int(chaosStartTime) > minTimeInChaos ):
            chaos = random.randrange( 100 )
            if( chaos > sensitivity ):
                print("OUT OF CHAOS MODE NOW FOR " + appToFail)
                chaosMode = False
    
        for app in apps:
            for hst in range( appCounts[ i ] ):
                if( chaosMode == True and ( app == appToFail or appImpactRegex in app ) ):
                    cpu_idle = str( 100 - random.randrange(80,100) )
                    mem_util = str( random.randrange(80,100) )
                    txnCount = random.randrange(5,1000)
                    errCount = str( random.randrange(int(txnCount/2), txnCount) )
                    hostName = app + "-" + str(hst)
                else:
                    cpu_idle = str( 100 - random.randrange(0,10) )
                    mem_util = str( random.randrange(10,30) )
                    txnCount = random.randrange(75000,100000)
                    errCount = str( random.randrange(0, int(txnCount/5)) )
                    hostName = app + "-" + str(hst)
    
                s = str( epochTime ) + "," + app + "," + hostName + "," + cpu_idle + "," + mem_util + "," + str( txnCount ) + "," + errCount + "\n"
                f.write( s )
            i += 1
    
        timeStamp = timeStamp - timedelta(minutes=1)
    f.close()

print("DONE")