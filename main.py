import socket
import threading

clients = {}
client_names = {}


def name_discon(name: str, client_socket: socket):
    """
    Отключение пользователя
    :param name:
    :param client_socket:
    :return:
    """
    try:
        client_socket.send("\t\t\tУведомление для вас.".encode())
        client_socket.close()
        del clients[client_socket]
        for key, value in list(client_names.items()):
            if value[0] == client_socket:
                del client_names[key]
                break
        broadcast(f"{name} покинул чат.")
        if name in client_names:
            del client_names[name]
        if client_socket in clients:
            del clients[client_socket]
    except (ConnectionAbortedError, TypeError, OSError):
        print("Успешное отключение клиента.")


def disconnect_user(ip: str, port: str) -> None:
    """
    Отключение пользователя через командную строку
    :param ip:
    :param port:
    :return:
    """
    for name, (client_socket, addr, p) in client_names.items():
        if addr == ip and p == port:
            name_discon(name, client_socket)
            return
    print("Такого клиента больше с нами нет ).")


def diss_input() -> None:
    """
    Функция для ввода IP и PORT
    :return:
    """
    while True:
        command = input()
        if command == "\\dis":
            ip_port = input("Введите IP PORT пользователя: ")
            address = ip_port.split()
            if len(address) == 2:
                ip = address[0]
                try:
                    port = int(address[1])
                    disconnect_user(ip, port)
                except (ValueError, OSError):
                    print("Недопустимый номер порта")


def handle_client(client_socket: socket, client_address: list) -> None:
    """
    Функция для работы с клиентами
    :param client_socket:
    :param client_address:
    :return:
    """
    name = ""
    while True:
        try:
            client_message = client_socket.recv(1024).decode()
            if not client_message:
                break
            if not name:
                if not client_message.strip():
                    client_socket.send("Имя не может быть пустым. Пожалуйста, выберите другое.".encode())
                elif client_message in client_names:
                    client_socket.send("Это имя уже занято. Пожалуйста, выберите другое.".encode())
                else:
                    name = client_message
                    clients[client_socket] = (client_address, name)
                    client_names[name] = (client_socket, client_address[0], client_address[1])
                    print(f"Подключенный клиент: {name} ({client_address[0]}:{client_address[1]})")
                    broadcast(f"{name} присоединился к чату.", client_socket)
            else:
                broadcast(f"\r\r{name}: {client_message}", client_socket)


        except (ConnectionResetError, OSError) as e:
            print("Произошла ошибка при обработке клиента:", str(e))
            if name:
                disconnect_user(client_address[0], client_address[1])
                if name in client_names:
                    del client_names[name]
                if client_socket in clients:
                    del clients[client_socket]
                    broadcast(f"{name} покинул чат.", client_socket)  # Отправляем сообщение о покидании чата
            break
    if name:
        name_discon(name, client_socket)


def broadcast(message: str, sender_socket: list) -> None:
    """
    Проверка, если клинта нету, то он не получит сообщение

    :param message:
    :param sender_socket:
    :return:
    """
    for client_socket in clients.keys():
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode())
            except (ConnectionResetError, OSError) as e:
                print("Произошла ошибка при передаче сообщения:", str(e))
                name_discon(client_names[sender_socket][1], sender_socket)


def start_server() -> None:
    """
    Запуск сервера
    :return:
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 5555))
    server_socket.listen(5)
    print("[Сервер начал работу]")

    diss_thread = threading.Thread(target=diss_input)
    diss_thread.start()

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
        except (ConnectionAbortedError, OSError) as e:
            print("Произошла ошибка при приеме клиентского подключения:", str(e))


if __name__ == '__main__':
    start_server()
