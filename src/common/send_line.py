def send_line(message, socket):
    socket.sendall(f'{message}\n'.encode('utf-8'))
