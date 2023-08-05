Triz2sce
********

Triz2sce versión 1.0.1 180420 (c) 2018 Pedro Fernández

Triz2sce.py es un script de Python 3.x que transforma un fichero generado con la utilidad para mapear aventuras Trizbort en un código fuente compatible con el compilador del DAAD.
No es un diseñador visual de aventuras ni una aplicación para su desarrollo completo. Está concebido como herramienta para hacer prototipos iniciales de aventuras con rapidez y facilidad y, a su vez, como herramienta de apoyo a autores nóveles, ideal para su uso en talleres de aprendizaje.

Uso:
====

Usar "Python triz2sce.py -h" en una linea de comandos o powershell para ver las opciones.

El script requiere como argumentos un fichero de entrada (que debe ser un mapa generado por la utilidad Trizbort en formato XML, con soporte para la versión 1.7.0) y el nombre de un fichero de salida, que será un código fuente en formato .SCE compatible con la versión 2.40 del compilador del DAAD.

La opción -p1 generará un listado SCE con los mensajes del sistema en primera persona. Por defecto éstos se crearán en segunda persona.

- Trizbort:

 - http://www.trizbort.com/

- DAAD

 - http://wiki.caad.es/DAAD
 - http://www.caad.es/fichas/daad.html (descarga)


Hasta el momento parece convertir correctamente:

- Habitaciones, incluyendo sus descripciones y estableciendo la localidad de comienzo.
- Conexiones comunes por puntos cardinales (N,S,E,O,NE,NO,SE,SO).
- Conexiones up/down o in/out.
- Conexiones de una sola dirección.
- Objetos incluidos en las habitaciones.

Triz2sce añade por su cuenta una barra de estado con el nombre de la localidad actual y el número de turnos transcurridos en la aventura.
También añade un listado automático de salidas y soporte para respuestas por defecto a los comandos "MIRAR","EXAMINAR" y "AYUDA".

Triz2sce usa los textos del cuadro de diálogo "map settings" (menu "tools") como pantalla de presentación, créditos y texto de introducción a la aventura (añadiendo frases por defecto en caso de que estuviesen vacíos).

A su vez usará el campo "subtitle" de cada localidad como texto para su descripción corta en la barra de estado (máximo 26 caracteres). Si no lo hubiera usará el campo "name" y si éste fuera el elegido por defecto "Cave" lo cambiará por "Localidad xx". A su vez usará el campo "description" para la descripción larga de la localidad en la ventana de texto de la aventura (usando de nuevo un texto por defecto "Descripción localidad xx" si no encontrase ninguno).

Igualmente triz2sce leerá, si los hubiera, los atributos [m], [f], [1], [2] y [w] en el nombre de los objetos, entendiéndolos como masculino, fememnino, singular, plural y ropa, y añadirá el artículo indeterminado correspondiente (un, uno, una, unas) al comienzo del texto de los objetos en la sección /OTX. Tanto si los hay como si no, entenderá la primera palabra del texto como la palabra de vocabulario para ese objeto y el texto completo como texto para su uso en listados.

Y por el momento triz2sce no puede manejarse con:

- Textos personalizados en los extremos de las conexiones, así como el resto de características personalizables de dichas conexiones en Trizbort (puertas, oscuridad) que al fin y al cabo tampoco tienen un soporte universal en los distintos formatos de fichero a los que Trizbort puede exportar.
- Conexiones con puntos intermedios en los espacios del mapa. Cualquier cosa que no sea una conexión directa entre una habitación y otra la ignorará.

PENDIENTE
=========

- Averiguar si hay opción de que Python saque el output del programa instalado por el powershell de Windows en lugar de abrir su propia ventana de comandos.
- Usar un fichero de salida por defecto a partir del nombre del de entrada y no tener que especificarlo obligatoriamente.
- Hacer que el contador de turnos pase a 0 tras 65535 en lugar de 65200 y algo.

HISTORIA
========

- **1.0.1** 180420

  - Añadida forma imperativa pronominal al verbo "poner"
  - Añadido soporte al atributo [w] (que entenderá como "wearable")

- **1.0** 180404

 - Primer lanzamiento.

- **Beta 0.9.1** 180402

 - Filtra acentos en el campo "author" antes de pasarlo a mayúsculas (las mayúsculas acentuadas no son admimtidas por el compilador del DAAD).
 - Añadida el verbo "AYUDA" al vocabulario e implementada su correspondiente acción.

- **Beta 0.9** 180331

 - Añadida barra de estado que muestra el atributo "subtitle" de la localidad y el nº de turnos ejecutados durante el juego.
 - Añadido soporte para el verbo "EXAMINAR" con respuesta por defecto.
 - El texto de los objetos de la sección /OTX añade artículos indeterminados (un, unos, una, unas) en función de los atributos de los objetos.

- **Beta 0.6** 180315

 - Listado de salidas deja de ser opcional (el aprendiz puede aprender a retirarlo manualmente con facilidad, lo que es más acorde con el carácter de herramienta de aprendizaje de triz2sce)
 - Se usan los textos del cuadro de diálogo "map settings" (menú tools) de trizbort como pantalla de presentación y créditos de la aventura.

- **Beta 0.5** 181103

 - Números de vocabulario diferentes para las acciones EXAMINAR y MIRAR
 - Corregido bug por el que se producía un error al intentar convertir mapas sin objetos (a base de añadir un objeto dummy)
 - Añadido listado automático de salidas (opcional) que, ojo, gasta los flags 100 y 101



