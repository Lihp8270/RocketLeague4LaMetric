import socket
import sys
import time

def sendData(command):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('rPi IP', rpi Port)
    print('connecting to %s port %s' % server_address, file=sys.stderr)
    sock.connect(server_address)

    try:
        # Send data
        message = command.encode()
        sock.sendall(message)

        # Look for the response
        global data 
        data = sock.recv(16)
        if '000'.encode() in data:
            print('Server NOT running')
        elif '111'.encode() in data:
            print('Server IS running')
        elif '222'.encode() in data:
            print('Server is STOPPING')
        elif 'starting'.encode() in data:
            print('Server is starting')
        elif 'stopping'.encode() in data:
            print('Server is stopping')
        elif '555'.encode() in data:
            print('ERROR: Cannot start, server is already running')
        elif '666'.encode() in data:
            print('ERROR: Cannot stop, server is not running')
    finally:
        print('closing socket', file=sys.stderr)
        sock.close()

if len(sys.argv) == 1:
    sendData('status')
    time.sleep(5)
    if '000'.encode() in data:
        print('server NOT running: attempting to start')
        sendData('start')
    elif '111'.encode() in data:
        print('server is running: attempting to stop')
        sendData('stop')
    else:
        print(data)
        print('ERROR: Please try with arguments, start, stop or status')
else:
    userInput = sys.argv[1]

    if userInput == 'start' or userInput == 'stop' or userInput == 'status':
        sendData(userInput)
    else:
        print('incorrect command: ')
        print(userInput)