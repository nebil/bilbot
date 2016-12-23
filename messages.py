"""
This module stores all the messages sent from Bilbot.

Copyright (c) 2016, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

from argparse import Namespace
from textwrap import dedent


# ERROR MESSAGES
# ===== ========

ERROR = Namespace(**{
    'NOT_AUTHORIZED':     dedent("""
                          Lo lamento, {user}.
                          No estoy autorizado a escuchar tus instrucciones.
                          """),
    'ALREADY_OPENED':     "Ya existe un periodo abierto, terrícola.",
    'WRONG_ARGUMENT':     "El argumento `{argument}` es incorrecto.",
    'MISSING_AMOUNT':     "Debes agregar el monto, terrícola.",
    'UNSOUND_AMOUNT':     "El monto es inválido.",
    'TOO_MANY_ARGUMENTS': "No te entiendo, humano.",
    'NONPOSITIVE_AMOUNT': "El argumento debe ser estrictamente positivo.",
    'UNREALISTIC_AMOUNT': "El argumento no es suficientemente razonable.",
    'NO_STORED_ACCOUNTS': "No hay registros disponibles.",

    'UNKNOWN_COMMAND': dedent("""
                       El comando `{command}` no existe.
                       Escribe `/help` para obtener una lista de comandos.
                       """),
})


# INFO MESSAGES
# ==== ========

INFO = Namespace(**{
    'START': "Bilbot, operativo.",
    'ABOUT':          dedent("""
                      Hola, mi nombre es Nebilbot.
                      Pero también me puedes llamar Bilbot.
                      Mi versión es `{version}`.
                      """),
    'ABOUT_RELEASES': dedent("""
                      Bueno, he tenido bastantes versiones en mi vida...
                      {releases}

                      Puedes, además, escribir `/about <versión>`,
                      para recibir el _changelog_ de esta versión.
                      """),
    'HELP': dedent("""
            Mis comandos son:
            {commands}
            """),

    # from Latin: 'ante' --> before,
    #             'post' --> after.
    'POST_NEW': "Muy bien, {user}. He abierto un nuevo periodo de compras.",

    'POST_CLEAR': "Todo listo: he eliminado cualquier rastro de registros.",

    'ANTE_WITHDRAW': "¿Estás seguro de que deseas retirar *{amount}* pesos "
                     "del quiosco, {user}?",
    'POST_WITHDRAW': "En realidad, da lo mismo: ya hice la operación.",
    'POST_ROLLBACK': "Estamos listos: ya revertí la última operación.",

    'ANTE_LIST': "Espera un poco, haré memoria de los hechos.",
    'EACH_LIST': "{user} sacó ${amount}.",
    'POST_LIST': dedent("""
                 Eso es todo lo que recuerdo.
                 Por cierto, esto suma un gran total de...
                 *{amount}* pesos chilenos.
                 """),
    'POST_AGGREGATE_LIST': "Además, si agregamos por cada humano...",
})
