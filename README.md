
# bilbot

Un bot del DCC para Telegram.  
Un bot de Telegram para el DCC.  
Para el DCC, de Telegram, un bot.  
Porque todo eso... es **bilbot**.

(Ya, no tenía idea qué escribir acá.)

## Receta

### Ingredientes

:snake: [Python] será nuestra herramienta de trabajo.  
:warning: Para evitar posibles fallas de compatibilidad,
se **deberá** usar una versión de Python superior a **3.3**.

#### Librerías de Python

La librería utilizada está resumida en la siguiente tabla.

Nombre                | Descripción                                 | Versión
--------------------- | ------------------------------------------- | ---------
[python-telegram-bot] | Un _wrapper_ del [API] de _Telegram Bot_.   | **5.1.0**

Esta librería también aparece en `requirements.txt`.
Luego, se **deberá** usar este archivo para instalarla con [pip].  
Esto nos permitirá trabajar con la misma versión,
consiguiendo instalaciones **replicables**, sin hacer esfuerzo.  
Bueno, un poco: debemos escribir...

```sh
$ pip install -r requirements.txt
```

En efecto, esto es... _as easy as **py**_. :grinning:

### Preparación

Para utilizar a Bilbot localmente, debes seguir los siguientes pasos.

1. :sheep:
   Clona el repositorio. Luego, accede.

   ```sh
   $ git clone https://github.com/nkawasg/bilbot.git
   $ cd bilbot
   ```

2. :wrench:
   Genera un entorno virtual de Python v3.**X** con [virtualenv].
   En este caso, se llamará `venv`.  
   No olvides que **X** debe ser: {3, 4, 5}.

   ```sh
   $ virtualenv --python=python3.X venv
   ```

3. :arrow_forward:
   Activa el entorno virtual.

   ```sh
   $ source venv/bin/activate
   ```

4. :white_check_mark:
   Instala las dependencias con [pip].

   ```sh
   $ pip install -r requirements.txt
   ```

5. :wrench:
   Configura el archivo `pseudo-bilbot.cfg` con el _token_ de tu bot.  
   Luego, elimina el prefijo `pseudo-` del archivo.

6. :snake:
   Ejecuta el _script_.

   ```sh
   $ python3 bilbot.py
   ```

7. :tada:
   _Voilà!_  
   Ahora, Bilbot debería estar encendido.

## Licencia

Copyright © 2016, Nebil Kawas García  
El código de este repositorio está bajo el [Mozilla Public License v2.0](
https://www.mozilla.org/MPL/2.0/).

[/]:# (Referencias implícitas)

[api]:                 https://core.telegram.org/bots/api
[python]:              http://www.pyzo.org/_images/xkcd_python.png

[python-telegram-bot]: https://pypi.python.org/pypi/python-telegram-bot
[virtualenv]:          https://virtualenv.pypa.io/en/stable
[pip]:                 https://pip.pypa.io/en/stable
