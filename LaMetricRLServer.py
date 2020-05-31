import requests
from bs4 import BeautifulSoup
import socket
import threading
import sys
import time
from queue import Queue

def threadWebScrape(stopQueue):
    def sendNotification(notificationMessage):
        headers = {
                'Content-Type': 'application/json',
            }

        data = '{ "model": { "frames": [ { "icon":"4540", "text":"'+notificationMessage+'"} ] } }'
        response = requests.post('LaMetric Notifiction address', headers=headers, data=data, auth=('dev', 'Notification key'))

    i = 1 # Set i as 1 for infinite loop
    sleepDuration = 180 # Polling time in seconds (Next wait if a cURL push has been made)
    noPushSleepDuration = 180 # Polling time in seconds (increases if no cURL push is made)
    maxSleepDuration = 1800 # Max duration between if no cURL push
    sleepDurationMultiplier = 1.2 # Rate at which polling time increases
    firstLoopFlag = 1 # Flag to prevent erroneous first notification
    noPushCounter = 0 # For exiting program after excessive no pushes

    # Initialise starting MMR
    prevDuelMmr = 10
    prevDblMmr = 10
    prevStdMmr = 10
    prevSoloMmr = 10

    # URL Here for scraping MMR
    URL = '####################'
    
    while i < 5: # Main loop for application - Polling increase each time there's no increase to max of 30 minutes
        # Check to stop program first
        queueVal = stopQueue.get()
        stopQueue.task_done()
       
        if queueVal == 0:
            sendNotification('STOPPING RL SERVICE')
            break

        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        rows = # REDACTED to prevent spam of my chosen source, but you need to Find MMRs in table
        rowsAsString = # REDACTED Convert to string so it can be split

        stringArray = rowsAsString.split() # Split at whitespace to separate MMR into array
    
        # Set Current MMR variables
        currentDuelMmr = stringArray[2]
        currentDblMmr = stringArray[7]
        currentStdMmr = stringArray[12]
        currentSoloMmr = stringArray[17]

        if prevDuelMmr != currentDuelMmr or prevDblMmr != currentDblMmr or prevStdMmr != currentStdMmr or prevSoloMmr != currentSoloMmr:
            # Build notification
            mmrUpdateMessage = 'MMR UPDATE: '
            if prevDuelMmr != currentDuelMmr:
                duelMmrDelta = int(currentDuelMmr) - int(prevDuelMmr)
                mmrUpdateMessage = mmrUpdateMessage+'DUEL: '+str(duelMmrDelta)+ ' /// '

            if prevDblMmr != currentDblMmr:
                dblMmrDelta = int(currentDblMmr) - int(prevDblMmr)
                mmrUpdateMessage = mmrUpdateMessage+'DBL: '+str(dblMmrDelta)+ ' /// '

            if prevStdMmr != currentStdMmr:
                stdMmrDelta = int(currentStdMmr) - int(prevStdMmr)
                mmrUpdateMessage = mmrUpdateMessage+'STD: '+str(stdMmrDelta)+ ' /// '

            if prevSoloMmr != currentSoloMmr:
                soloMmrDelta = int(currentSoloMmr) - int(prevSoloMmr)
                mmrUpdateMessage = mmrUpdateMessage+'SOLO: '+str(dblMmrDelta)+ ' /// '

            # Check if this is the first loop and display a different notification
            if firstLoopFlag == 1:
                sendNotification('rPi service now online')
            else:
                ## MMR Update Notification
                sendNotification(mmrUpdateMessage)
      
            time.sleep(5)
            
            ## Format JSON for Push
            headers = {
                'Accept': 'application/json',
                'X-Access-Token': 'Your Token',
                'Cache-Control': 'no-cache',
            }

            data = '{\n    "frames": [\n        {\n            "text": "Duel: '+str(currentDuelMmr)+'",\n            "icon": null\n        },\n        {\n            "text": "DBL: '+str(currentDblMmr)+'",\n            "icon": null\n        },\n        {\n            "text": "STD: '+currentStdMmr+'",\n            "icon": null\n        },\n        {\n            "text": "Solo: '+currentSoloMmr+'",\n            "icon": null\n        }\n    ]\n}'
            response = requests.post('LaMetric Push URL', headers=headers, data=data)
        
            # Set current MMR as previous to prevent repushing repeated data
            prevDuelMmr = currentDuelMmr
            prevDblMmr = currentDblMmr
            prevStdMmr = currentStdMmr
            prevSoloMmr = currentSoloMmr

            # Turn flag off for incorrect first notification
            firstLoopFlag = 0

            # Reset No-Push variables
            noPushCounter = 0
            noPushSleepDuration = 180

            statusQueue.put(1) # Required to stop thread stalling
            time.sleep(sleepDuration)
        else:
            noPushCounter = noPushCounter + 1
            if noPushCounter > 15:
                sendNotification('rPi Service stopped due to no push - Restart service if required')
                break
            if noPushCounter > 5:
                noPushSleepDuration = 420

            statusQueue.put(1) # Used to stop thread stalling
            time.sleep(noPushSleepDuration)  
            if noPushSleepDuration < maxSleepDuration:
                noPushSleepDuration = noPushSleepDuration * sleepDurationMultiplier
            else:
                noPushSleepDuration = maxSleepDuration

status = 0
statusQueue = Queue()
isRunning = 0

# Create a TCP/IP Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print ('Starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)

# Listen for incoming connection
sock.listen(1)

# Set up worker thread
worker = threading.Thread(target=threadWebScrape, args=(statusQueue,), daemon=True)
threadState = worker.is_alive()

while True:
        # Wait for a connection
        print('waiting for a conenction', file=sys.stderr)
        connection, client_address = sock.accept()

        try:
            print('connection from', client_address, file=sys.stderr)

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                if 'status'.encode() in data:
                    threadState = worker.is_alive()
                    if threadState == 1:
                        responseStatus = '111'.encode()
                        if status == 0:
                            responseStatus = '222'.encode()
                    elif threadState == 0:
                        responseStatus = '000'.encode()
                    else:
                        reponseStatus = 'Cannot get status'.encode()

                    print('sending status to client', file=sys.stderr)
                    connection.sendall(responseStatus)

                elif 'start'.encode() in data:
                    if threadState == 1:
                        print('Cannot start server - already running', file=sys.stderr)
                        connection.sendall('555'.encode())
                    else:
                        print('Starting rPi service', file=sys.stderr)
                        connection.sendall('starting'.encode())
                        
                        # Start thread and set status
                        status = 1
                        statusQueue.put(status)
                        threadState = worker.is_alive()
                        worker.start()

                elif 'stop'.encode() in data:
                    if threadState == 0:
                        print('Cannot stop server - not running', file=sys.stderr)
                        connection.sendall('666'.encode())
                    else:
                        # Stop thread and set status
                        status = 0
                        statusQueue.put(status)
                        print('Stopping rPi service', file=sys.stderr)
                        connection.sendall('stopping'.encode())
                else:
                    print('no more data from client', client_address, file=sys.stderr)
                    threadState = worker.is_alive()
                    break          
        finally:
            # Clean up the connection
            connection.close()