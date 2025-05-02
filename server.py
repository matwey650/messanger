import socket
import threading

HOST = "localhost"
PORT = 8080

clients = []

def broadcast (data, exlusive_socket):
    for client in clients:
        if client != exlusive_socket:
            try:
                client.sendall(data)
            except:
                pass

def hendle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break
            broadcast(data, client_socket)
        except:
            break
    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,  1)
sock.bind((HOST, PORT))
sock.listen(5)
print(f"сервер запущено на {HOST} : {PORT}")
while True:
    client, adress = sock.accept()
    print(f"пидключився {adress}")
    clients.append(client)
    t = threading.Thread(target = hendle_client, args = (client,))
    t.start()








