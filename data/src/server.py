import threading
import socket

class Server:

    def __init__(self):
        HOST = '' 
        PORT = 3389
        ADDR = (HOST, PORT)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)

        self.clients = []
        self.active_pairings = [[],[],[],[],[],[],[],[],[],[]]
        self.rooms = [0,1,2,3,4,5,6,7,8,9]


    def listen(self):
        self.server.listen()
        while True:
            client, address = self.server.accept()
            self.clients.append(client)

            print(f"{address} has joined the server")

            if len(self.clients) >= 2:
                for client in self.clients:
                    try:
                        client.send("ISACTIVE".encode('ascii'))
                        resp = client.recv(64).decode('ascii')
                    except: 
                        self.clients.remove(client)
                if len(self.clients) >= 2:
                    pairs = len(self.clients) // 2
                    for _ in range(pairs):
                        room = min(self.rooms)
                        self.active_pairings[room].append(self.clients[:2])
                        for client in self.clients[:2]:
                            try:
                                client.send('FOUND'.encode('ascii'))
                            except:
                                break
                            threading.Thread(target=self.handle_client, args=(client,room)).start()
                        self.clients = self.clients[2:]
                        self.rooms.remove(room)


    def handle_client(self, client, room): 
        pair = self.active_pairings[room][0]
        print(pair)
        client_index = pair.index(client)
        while True: 
            try:
                data = client.recv(64) 
                if data.decode('ascii') == "LEAVING":
                    pair[client_index-1].send("LOST_OPP".encode('ascii'))
                    self.active_pairings[room] = []
                    self.rooms.append(room)
                    break
                elif data.decode('ascii') == "FINISHED":
                    self.active_pairings[room] = []
                    self.rooms.append(room)
                    break
                elif data.decode('ascii') == "STEAL":
                    pair[client_index-1].send("STOLEN".encode('ascii'))
                else:
                    pair[client_index-1].send(data)
            except:
                self.active_pairings[room] = []
                self.rooms.append(room)
                try:
                    client.send("ERROR".encode('ascii'))
                    pair[client_index-1].send("ERROR".encode('ascii'))
                except:
                    client.close()
                    pair[client_index-1].close()
                    break
                break 



server = Server()
server.listen()
