
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

#### Archivos

Los archivos del repositorio están resumidos en la siguiente tabla.

Nombre             | Descripción
------------------ | ------------------------------------------
`.gitignore`       | Archivos ignorados por Git.
`.pylintrc`        | _Config-file_ de `pylint`.
`bilbot.cfg`       | _Config-file_ de `bilbot`.
`bilbot.py`        | Módulo esencial de Bilbot.
`changelog.py`     | Módulo con el _changelog_.
`messages.py`      | Módulo con los mensajes para los usuarios.
`LICENSE`          | Documento con el Mozilla Public License.
`README.md`        | `self`
`requirements.txt` | Archivo de dependencias para `pip`.
`tox.ini`          | _Config-file_ de `flake8`.

#### Librerías de Python

Las librerías utilizadas están resumidas en la siguiente tabla.

Nombre                | Descripción                                 | Versión
--------------------- | ------------------------------------------- | ---------
[python-telegram-bot] | Un _wrapper_ del [API] de _Telegram Bot_.   | **5.3.0**
[flake8]              | Un _linter_ para hacer respetar el [PEP8].  | **2.6.2**
[pylint]              | Un _linter_ que impone _buenas prácticas_.  | **1.6.4**

Estas librerías también aparecen en `requirements.txt`.
Luego, se **deberá** usar este archivo para instalarlas con [pip].  
Esto nos permitirá trabajar con las mismas versiones,
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
   Configura el archivo `bilbot.cfg` con el _token_ de tu bot.

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
[flake8]:              https://pypi.python.org/pypi/flake8
[pylint]:              https://pypi.python.org/pypi/pylint
[pep8]:                https://www.python.org/dev/peps/pep-0008
[virtualenv]:          https://virtualenv.pypa.io/en/stable
[pip]:                 https://pip.pypa.io/en/stable
