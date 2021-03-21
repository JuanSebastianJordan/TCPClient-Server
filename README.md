# TCPClient-Server

1. Clone el repositorio en su maquina local. Elija una maquina donde correr el servidor y otra en donde correr el cliente. Este programa tambien puede ser ejecutado ambos programas en la misma maquina.
2. Asegurarse que en el ambiente donde se decida correr la aplicación cuente con python y pip instalados
3. Una vez clonado el repositorio navegue a esa carpeta Server o Client dependiendo de cual va a ejecutar.
4. Descargue los archivos que se van a transferir del siguiente link para el archivo de 100 MB https://www.dropbox.com/s/qc5erqchyhhj84r/File1.mp4?dl=0. Para el archivo de 250 MB use el siguiente link https://www.dropbox.com/s/nawghvadzsy7opk/File2.mp4?dl=0. 
5. Asegurese de copiar estos archivos en la carpeta Server/data/Files. Con los nombres File1.mp4 para el archivo de 100 MB y File2.pm4 para el archivo de 250 MB.
6. Una vez en esa carpeta instale los requirements del cada proyecto. Para eso ejecute "pip install -r requirements.txt"
7. Una vez hecho esto ya puede ejecutar cualquiera de los dos programas. Para esto ejecute "python client.py" o "python server.py"
8. El el servidor antes de empezar la ejecución le debera indicar el archivo que quiere transferir y la cantidad de clientes.
9. Para el cliente debe ejecutar tantas veces como clientes quiera para su prueba. Es decir si desea 5 clientes debe abrir 5 consolas de comando, por ejemplo.
