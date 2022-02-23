import os
import socket

REDIRECTION_DICTIONARY = {'/js/box1.js': '/js/box.js'}
GOOD_STATUS = "200 OK"
MSG_SIZE = 1024
IP = "0.0.0.0"
PORT = 80
SOCKET_TIMEOUT = 1
WEBROOT_ROOT = "c:\\cyber\\webroot"
VERSION = "HTTP/1.1"
EOL = "\r\n"
DEFAULT_RESOURCE = "C:\\Cyber\\webroot\\index.html"


def valid_file(path):
    """
    a method that's claim a name and check if it is a file
    """
    return os.path.isfile(path)


def handle_client(client_socket):
    print('Client connected')
    done = False
    while not done:
        raw_client_request = client_socket.recv(MSG_SIZE)
        client_request = raw_client_request.decode()
        done = (client_request == '')
        if not done:
            status, resource = validate_http_request(client_request)
        handle_client_request(resource, client_socket, status)


def initiate_server_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(10)
    print("Listening for connections on port %d" % PORT)
    return server_socket


def handle_clients(server_socket):
    """ loop forever while waiting for clients """
    client_socket = None
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print('New connection received')
            client_socket.settimeout(0.5)
            handle_client(client_socket)
        except socket.error as e:
            print("client failed", e)
            client_socket.close()


def handle_client_request(resource, client_socket, status):
    print(' requested resource: ', resource)
    # retrieve file content and content type
    if status == "200 OK":
        data, content_type_str = file_request(resource)
        data_size = str(len(data))
        http_header = 'HTTP/1.1 ' + status + EOL + \
                      'Content-Length: ' + data_size + EOL + \
                      content_type_str + \
                      EOL + EOL
    # finally constructing header
    if status == "302 Moved Temporarily":
        http_header = 'HTTP/1.1  ' + status + EOL + \
                      "Location" + REDIRECTION_DICTIONARY[resource]
    if status == "404 Not Found":
        http_response = VERSION + " " + status + EOL + EOL
        http_response = http_response.encode()
    else:
        print(http_header)
        http_response = http_header.encode() + data
    client_socket.send(http_response)


def validate_http_request(request):
    """
    validates the http request:
    1- starts with GET
    2 - ends with HTTP/1.1
    3 - holds a valid resource name between both of them
    returns a tuple -
    boolean: isValid
    retrieved resource name
    """
    # change the request to a list
    ls_req = request.split()
    # makes a file root combined from the file root and the webroot root
    file_root = WEBROOT_ROOT + ls_req[1]
    if ls_req[0] == "GET" and ls_req[2] == "HTTP/1.1" and ls_req[1] == "/":
        return GOOD_STATUS, DEFAULT_RESOURCE
    if ls_req[1] in REDIRECTION_DICTIONARY.keys():
        return "302 Moved Temporarily", REDIRECTION_DICTIONARY[ls_req[1]]
    if not valid_file(file_root):
        return "404 Not Found", None
    if ls_req[0] == "GET" and ls_req[2] == "HTTP/1.1" and valid_file(file_root):
        return GOOD_STATUS, ls_req[1]
    if "calculate" in ls_req[1]:
        ls_of_request = ls_req[1].split("=")
        number = ls_of_request[-1]
        return GOOD_STATUS, calculate_next(number)
    if "calculate-area" in ls_req[1]:
        num1 = ls_req[1][ls_req[1].find("=") + 1]
        num2 = ls_req[1][ls_req[1].find("=", num1 + 1, len(ls_req[1])) + 1]
        return GOOD_STATUS, calculate_area(num1, num2)
    return "500 Server Internal Error", None


def calculate_area(height, width):
    return (width * height) / 2


def calculate_next(number):
    """

    :param number:
    :return: num plus 1
    """
    return number + 1


def file_request(resource):
    resource_ls = resource.split(".")
    content_type = resource_ls[-1]
    if content_type == "txt" or content_type == "html":
        content_type = "text/html; charset=utf-8"
    if content_type == "jpg" or content_type == "ico" or \
            content_type == "gif" or content_type == "png":
        content_type = "image/jpeg"
    if content_type == "css":
        content_type == "text/css"
    if content_type == "js":
        content_type = "text/javascript; charset=utf-8"
    if resource != DEFAULT_RESOURCE:
        resource = WEBROOT_ROOT + "\\" + resource
    my_file = open(resource, "rb")
    my_file = my_file.read()
    return my_file, content_type


def main():
    """
    server main - receives a message returns it to
   client
    """
    # try:
    server_socket = initiate_server_socket()
    handle_clients(server_socket)
    server_socket.close()
    # except socket.error as msg:
    #     print("socket failure: ", msg)
    # except Exception as msg:
    #     print("exception: ", msg)


if __name__ == "__main__":
    main()
