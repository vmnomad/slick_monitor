import socket

hostname = 'google.com'
port = 80

obj = (hostname,port)
#obj.setdefaulttimeout(2)




try:
    tcp = socket.create_connection(obj, timeout=2)

    print('Connection is successful')
    tcp.close()
except Exception as er:
    print("TCP Connection Failed:", er)
