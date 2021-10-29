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

El cliente cuenta con dos acciones posibles, las cuales se detallan a continuación.

#### upload-file

Este comando es utilizado para subir archivos al servidor especificado.

```python
python upload-file.py [-h] [-v | -q] [-H host] [-p port] [-s source] [-n name] [-m mode]
```
A continuación se listarán los comandos para cada modo.

Argumentos posicionales:
*  **-H host:** dirección IP a la que se desea conectar.
*  **-p port:** puerto.
*  **-d dest:** ruta de archivo a subir.
*  **-n name:** nombre del archivo a subir.
*  **-m mode:** tipo de socket a utilizar {tcp, gbn: UDP GoBackN, sw: UDP Stop&Wait}.           

Argumentos opcionales:
*  **-h, --help:** muestra una descripción de los parámetros y finaliza la ejecución.
*  **-v, --verbose:** incrementa la verbosidad del output.
*  **-q, --quiet:** decrementa la verbosidad del output.

#### download-file
Este comando es utilizado para descargar archivos del servidor especificado.

```python
python download-file.py [-h] [-v | -q] [-H host] [-p port] [-d dest] [-n name] [-m mode]
```

Argumentos posicionales:
*  **-H host:** dirección IP a la que se desea conectar.
*  **-p port:** puerto.
*  **-d dest:** ruta de almacenamiento del archivo a descargar.
*  **-n name:** nombre del archivo a descargar.
*  **-m mode:** tipo de socket a utilizar {tcp, gbn: UDP GoBackN, sw: UDP Stop&Wait}.

Argumentos opcionales:
*  **-h, --help:** muestra una descripción de los parámetros y finaliza la ejecución.
*  **-v, --verbose:** incrementa la verbosidad del output.
*  **-q, --quiet:** decrementa la verbosidad del output.

### Servidor
El servidor cuenta con un único comando de ejecución:

```python
python start-server.py [-h] [-v | -q] [-H host] [-p port] [-s storage] [-m mode]
```

Argumentos posicionales:
*  **-H host:** dirección IP a la que se desea conectar.
*  **-p port:** puerto.
*  **-s storage:** ruta de almacenamiento de archivos del servidor.
*  **-m mode:** tipo de socket a utilizar {tcp, gbn: UDP GoBackN, sw: UDP Stop&Wait}.

Argumentos opcionales:
*  **-h, --help:** muestra una descripción de los parámetros y finaliza la ejecución.
*  **-v, --verbose:** incrementa la verbosidad del output.
*  **-q, --quiet:** decrementa la verbosidad del output.

### Aclaraciones adicionales
El enunciado del trabajo indica que el programa debe funcionar utilizando localhost, esto puede realizarse utilizando la ip 127.0.0.1 en las opciones de ip del programa.
