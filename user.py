import socket
import threading


def receive_messages(client_socket: socket) -> None:
    """
    Получение сообщение от других пользователей
    :param client_socket:
    :return:
    """
    try:
        while True:
            message = client_socket.recv(1024).decode()
            print(message)
    except (ConnectionRefusedError, ConnectionResetError):
        print("Вы были отключены от сервера")


def send_message(client_socket: socket) -> None:
    """
    Обработка сообщений пользователя
    :param client_socket:
    :return:
    """
    while True:
        try:
            message = input("")
            client_socket.send(message.encode())
        except ConnectionResetError:
            print("Соединение было неожиданно разорвано")
            break


def connect_to_server(ip: str, port: int) -> socket:
    """
    Проверка корректности подключения на сервер
    :param ip:
    :param port:
    :return:
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if ip == "0.0.0.0":
            print("Вы ввели некорректный IP. Пожалуйста, введите корректный IP.")
            return None
        client_socket.connect((ip, port))
        return client_socket
    except (ConnectionRefusedError, ConnectionResetError, OverflowError, socket.gaierror, OSError):
        print("Не удалось подключиться к серверу")
        return None


def main() -> None:
    """
    Основная реализация команд/сообщений
    :return:
    """
    while True:
        command = input("Введите команду (/connect для подключения, /exit для отключения): ")
        if command == "/connect":
            while True:
                server_ip = input("Введите IP сервера: ")
                server_port = input("Введите порт сервера: ")
                try:
                    server_port = int(server_port)
                    break
                except (ValueError, OSError):
                    print("Пожалуйста, введите корректный порт")

            client_socket = connect_to_server(server_ip, server_port)
            if client_socket:
                break
        elif command == "/exit":
            print("Выход из программы.")
            return
        else:
            print("Некорректная команда.")

    try:
        client_name = input("Введите своё имя: ")
        client_socket.send(client_name.encode())

        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        send_thread = threading.Thread(target=send_message, args=(client_socket,))
        send_thread.start()
    except (ConnectionResetError, OSError):
        print("Сервер на данный момент не активен.")


if __name__ == "__main__":
    main()