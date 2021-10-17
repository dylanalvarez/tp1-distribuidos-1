def receive_line(socket, must_exit=False):
    message = ''
    while not message.endswith('\n') or must_exit:
        message += socket.recv(10).decode('utf-8')
    if message.endswith('\n'):
        return message
    return None
