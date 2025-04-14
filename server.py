import threading
import socket
import argparse
import os

class Server(threading.Thread):
    
    def __init__(self, host, port):
        super().__init__()
        self.connections= []
        self.host = host
        self.port = port
        
    def run(self):
     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
     sock.bind((self.host, self.port))
     
     sock.listen(1)
     print("Listening at", sock.getsockname())
     
     while True:
         
         #Accepting New connections
         sc, sockname = sock.accept()
         print(f"Accepting new connection from {sc.getpeername()} to {sc.getsockname()}")
         
         # creating a new thread
         server_socket = ServerSocket(sc,sockname,self)
         
         #start a new thread
         
         server_socket.start()
         
         #add thread to active connection
         self.connections.append(server_socket)
         print("Ready to recieve messages from",sc.getpeername())
    
    def broadcast(self,message,source):
        for connection in self.connections():
            
            if connection.sockname != source: # send to all connected client accept the source client
                connection.send(message)
    
    def remove_connection(self,connection):
        self.connections.remove(connection)         
        
class ServerSocket(threading.Thread):
    def __init__(self, sc,sockname,server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server
        
    def run(self):
        
        while True:
            message = self.sc.recv(1024).decode('ascii')
            
            if message:
                print(f"{self.sockname} say {message}")
                self.server.broadcast(message,self.sockname)
                
            else:
                print(f"{self.sockname} closed the connection")
                Server.remove_connection(self)
                
    def sendmsg(self, message):
        self.sc.sendall(message.encode('ascii'))
        
def exit(server):
    
    while True:
        ipt = input("")
        if ipt == "q":
            print("Closing session")
            for connection in server.connections():
                connection.sc.close()
                
            print("shutting server")
            os.exit(0)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chatroom server")
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port(default 1060)')
    
    args = parser.parse_args()
    
    #create and start new thread
    
    server = Server(args.host, args.p)
    server.start()
    
    exit = threading.Thread(target=exit,args = (server,))
    exit.start()
                   