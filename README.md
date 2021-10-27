# FileTransfer-Intro
Trabajo Práctico 1 de la materia Introducción a los Sistemas Distribuidos (75.43) de la FIUBA.

### Integrantes
- Cambiano, Agustin - 102291
- Daverede, Agustin - 98540
- Martinez Sastre, Gonzalo - 102321
- Rolando, Marcos - 102323
- Soriano, Ivan - 120342

## Requisitos
Se listarán las diferentes bibliotecas necesarias para correr el proyecto
- [Python3](https://www.python.org/downloads/)

## Ejecución

### Cliente

Para ejecutar el cliente deberán ingresarse los comandos en la forma

```python
./client.py [-h] [-v | -q] [-H host] [-p port] [-d/-s dest/source] [-n name]
```

El cliente cuenta con dos modos de ejecución:

- upload-file         Upload a file to the specified server
- download-file       Download a file from the specified server

A continuación se listarán los comandos para cada modo.

#### upload-file

Positional arguments:
*  -H host           service IP address
*  -p port           service port
*  -s source         source file path
*  -n name           file name

Optional arguments:
*  -h, --help     show this help message and exit
*  -v, --verbose  increase output verbosity
*  -q, --quiet    decrease output verbosity

#### download-file
Positional arguments:
*  -H host           service IP address
*  -p port           service port
*  -d dest           destination file path
*  -n name           file name

Optional arguments:
*  -h, --help     show this help message and exit
*  -v, --verbose  increase output verbosity
*  -q, --quiet    decrease output verbosity

### Servidor
El servidor cuenta con un solo comando de ejecución

```python
./client.py [-h] [-v | -q] host port storage
```

Positional arguments:
*  -H host           service IP address
*  -p port           service port
*  -s storage        storage dir path

Optional arguments:
*  -h, --help     show this help message and exit
*  -v, --verbose  increase output verbosity
*  -q, --quiet    decrease output verbosity