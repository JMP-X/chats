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
        for connection in self.connections:
            
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
        try:
            message = self.sc.recv(1024)
            if not message:  # Connection closed by client
                print(f"{self.sockname} closed the connection")
                self.server.remove_connection(self)
                self.sc.close()
                break
                
            try:
                decoded_message = message.decode('ascii')
                print(f"{self.sockname} says {decoded_message}")
                self.server.broadcast(decoded_message, self.sockname)
            except UnicodeDecodeError:
                print(f"{self.sockname} sent non-ASCII data")
                continue
                
        except ConnectionResetError:
            print(f"{self.sockname} connection reset")
            self.server.remove_connection(self)
            self.sc.close()
            break
        except OSError as e:
            print(f"Error with {self.sockname}: {e}")
            self.server.remove_connection(self)
            self.sc.close()
            break
                
    def send(self, message):
        self.sc.sendall(message.encode('ascii'))
        
def exit(server):
    
    while True:
        ipt = input("")
        if ipt == "q":
            print("Closing session")
            for connection in server.connections:
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
                   