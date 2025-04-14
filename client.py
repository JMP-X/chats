import threading
import socket
import argparse
import os
import sys
import tkinter as tk

class Send(threading.Thread):
    # listens for user input from commandLine
    #sock the connected sock object 
    #name (Str): the username provided by user
    
    def __init__(self,sock,name):
        super().__init__()
        self.sock = sock
        self.name = name
        
    def run(self):
        #listen to input and send to server
        
        while True:
            print('{}:'.format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]
            
            #'DC' leaves the room
            
            if message == "DC":
                self.sock.sendall('Server: {} has left the session.'.format(self.name).encode('ascii'))
                break
            
            else:
                self.sock.sendall('{}: {} '.format(self.name,message).encode('ascii'))
                
        print('\n closing....')
        self.sock.close()
        os.exit(0)

class Recive(threading.Thread):
    # listen to server for incoming messages
    
    def __init__(self,sock,name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None
    
    def run(self):
        while True:
            message = self.sock.recv(1024).decode('ascii')
            
            if message:
                if self.messages:
                    self.messages.insert(tk.END, message)
                    print('Hello...')
                    print('\r{}\n{}: '.format(message,self.name),end='')
                    
                
                else:
                  print('\r{}\n{}: '.format(message,self.name),end='')
            
            else:
                print('\n Connection Lost...')
                print('\nTerminating.....')
                self.sock.close()
                os.exit(0)
                
class Client:
    
    #For managing client-Server connection and Integrate GUI
    
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.name = None
        self.messages = None
        
    
    def start(self):
        print('Attempting Connection to {}:{}'.format(self.host,self.port))
        
        self.sock.connect((self.host, self.port))
        print('\n Successfully connected to {}:{}'.format(self.host, self.port))
        print('\n')
        
        self.name = input(" Your Username: ")
        print(f'\nWelcome {self.name}!')
    
    # Send and Recive Threads
    
        send = Send(self.sock,self.name)
        ReciveMSG = Recive(self.sock,self.name)
    
        send.start()
        ReciveMSG.start()
    
        self.sock.sendall(f'Server: {self.name} joined the chat!'.encode('ascii'))
        print("\r Leave chatroom by typing 'DC")
        print(f'{self.name}:', end='')
    
    
        return ReciveMSG
    
    def send(self,TInput):
        # sends Input from GUI
        
        message = TInput.get()
        TInput.delete(0, tk.END)
        self.messages.insert(tk.END, '{}: {}'.format(self.name,message))
        
        #leave Room with 'DC'
        
        if message == 'DC':
         self.sock.sendall('Server: {} has left'.format(self.name).encode('ascii'))
         print('\nTerminating.....')
         self.sock.close()
         os._exit(0) 
        
        #send normal message
        else: 
            self.sock.sendall(f'{self.name}:{message}'.encode('ascii'))  


def main(host,port):
    #initialize and run GUI APP
    
    client = Client(host,port)
    recieve = client.start()
    
    window = tk.Tk()
    window.title(" The Chatroom ")
    
    fromMessage = tk.Frame(master=window)
    scrollB = tk.Scrollbar(master=fromMessage)
    messages  = tk.Listbox(master=fromMessage, yscrollcommand=scrollB.set)
    scrollB.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    client.messages = messages
    recieve.messages = messages
    
    fromMessage.grid(row=0,column=0, columnspan=2, sticky="nsew")
    FromEntry= tk.Frame(master=window)
    TextIn = tk.Entry(master=FromEntry)
    
    TextIn.pack(fill=tk.BOTH, expand=True)
    TextIn.bind("<Return>", lambda x: client.send(TextIn))
    TextIn.insert(0,"Message: ")
    
    buttonSend = tk.Button(master=window, text="Send", command=lambda: client.send(TextIn))
    
    FromEntry.grid(row=1,column=0, padx= 10,sticky="ew")
    buttonSend.grid(row=1,column=1, pady= 10,sticky="ew")
    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)
    
    window.mainloop()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chatroom server")
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port(default 1060)')
    
    args = parser.parse_args()
    
    main(args.host,args.p)
    
