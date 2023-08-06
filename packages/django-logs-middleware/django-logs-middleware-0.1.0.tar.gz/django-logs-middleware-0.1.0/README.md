# Logger Middleware

Es una libreria que permite almacenar en una base de datos de Mongo los eventos que son generados 
en los distintos recursos de tipo _REST_ de una aplicación realizada en Django


### Instalación

Se puede instalar como una libreria por medio de los siguientes medios:

1. Comando Pip

2. Repositorio en Github

#### Comando PIP

Se puede ejecutar el siguiente comando:

```
 pip install 
```

#### Repositorio

Si se tiene un archivo de `requirements.txt`, se puede generar la libreria por medio del código 
fuente del repositorio agregando la siguiente linea:

```
git+https://github.com/AirBit-Club/D220180414_logs-middleware
```




### Configuración

La librería _django-logger-middleware_ utiliza las configuraciones el archivo `settings.py` de un 
proyecto django. Las configuraciones que utiliza son:

 
| Llave | Requerido | Datos | Descripción |
| ----- |:---------:| :-----: | :----------- |
| APP_NAME | Opcional | String | Indica el nombre de la aplicación|
| LOGS | Opcional | Dictionary | Es un diccionario con las configuraciones personalizadas de la libreria|