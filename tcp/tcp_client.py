import socket
import argparse

serverName = "localhost"
serverPort = 12000

clientSocket = socket("AF_INET", "SOCK_STREAM")
clientSocket.connect((serverName, serverPort))

sentence = "Como estás papi?"
clientSocket.send(sentence.encode())

clientSocket.close()
