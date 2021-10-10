class FileReader:
    
    #Inicializa el objeto que lee el archivo, en caso de que falle la apertura
    #del archivo tira IOError
    def __init__(self, filename: str):
        self.file = open(filename, 'rb')

    #Lee y retorna hasta bytes_to_read bytes del archivo que se recibio en el constructor
    #Retorna un array de byteslike, en caso de que no quede nada por leer en el archivo
    #tira la excepcion EOFError
    def read_next_section(self, bytes_to_read: int):
        bytes_read = self.file.read(bytes_to_read)
        if bytes_read == b'':
            raise EOFError()
        return bytes_read

    #Cierra el archivo
    def close(self):
        self.file.close()
