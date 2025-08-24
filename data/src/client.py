
import socket
import threading

class Client:

    def __init__(self):
        HOST = '34.145.53.125'
        PORT = 49152
        self.ADDR = (HOST, PORT)

        self.values = set()
        self.value = 0
        self.opponent_value = 0

        self.has_pair = False
        self.lost_connection = False
        self.waiting = True

        self.show_activity = True

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connected = False
        self.want_to_connect = False
        self.connect_thread = threading.Thread(target=self.start)
        self.connect_thread.daemon = True

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.daemon = True
        self.write_thread = threading.Thread(target=self.write)
        self.write_thread.daemon = True

        self.connect_thread.start()
        self.receive_thread.start()
        self.write_thread.start()

        self.stolen = False
        self.sent = False


    def is_connection_lost(self):
        return self.lost_connection
    

    def delete(self):
        self.client.close()
        self.want_to_connect = False


    def disconnect(self):
        self.client.close()
        self.connected = False
        self.want_to_connect = False
        self.has_pair = False
        self.lost_connection = True

    
    def connect(self):
        self.want_to_connect = True
        self.lost_connection = False


    def start(self):
        while True:
            if self.want_to_connect:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client.connect(self.ADDR)
                self.connected = True
                self.want_to_connect = False
                self.waiting = False


    def opponent_found(self):
        return self.has_pair


    def receive(self):
        while True:
            if self.connected:
                try:
                    self.has_pair = self.client.recv(64).decode('ascii')
                    print(self.has_pair)
                except:
                    break
                
                if self.has_pair == "ISACTIVE":
                    self.client.send("ACTIVE".encode('ascii'))
                elif self.has_pair == "FOUND":
                    self.has_pair = True
                else:
                    self.has_pair = False

                while self.has_pair == True: 
                    try:
                        opponent_val = self.client.recv(64).decode('ascii')
                        if opponent_val == "ERROR" or opponent_val == "LOST_OPP":
                            self.disconnect()
                        elif opponent_val == "STOLEN":
                            self.stolen = True
                        else:
                            if opponent_val.isnumeric():
                                self.opponent_value = opponent_val
                    except:
                        self.disconnect()

    def write(self):
        while True:
            if self.connected:
                while self.has_pair:
                    if self.value not in self.values:
                        try:
                            self.client.send(str(self.value).encode('ascii'))
                        except:
                            self.disconnect()
                            
                        self.values.clear()
                        self.values.add(self.value)


    def set_value_data(self, value):
        self.value = value


    def send_server_message(self, message):
        self.client.send(message.encode('ascii'))
        self.sent = True