import os

from tinamit import _
from tinamit.EnvolturaMDS.Vensim import ModeloVensim, ModeloVensimMdl
from tinamit.EnvolturaMDS.PySD import ModeloPySD
from tinamit.MDS import EnvolturaMDS


dic_motores = {
    '.vpm': [ModeloVensim],
    '.mdl': [ModeloPySD, ModeloVensimMdl],
    '.xml': [ModeloPySD],
    '.xmile': [ModeloPySD]

    # Agregar otros tipos de modelos DS aquí.

}


def generar_mds(archivo):
    """
    Esta función genera una instancia de modelo de DS. Identifica el tipo de archivo por su extensión (p. ej., .vpm) y
    después genera una instancia de la subclase apropiada de :class:`~tinamit.EnvolturaMDS.EnvolturaMDS`.

    :param archivo: El archivo del modelo DS.
    :type archivo: str

    :return: Un modelo DS.
    :rtype: EnvolturaMDS

    """

    # Identificar la extensión.
    ext = os.path.splitext(archivo)[1]

    # Verificar si podemos leer este tipo de archivo.
    if ext not in dic_motores:
        # Mensaje para modelos todavía no incluidos en Tinamit.
        raise TypeError(_('El tipo de modelo "{}" no se acepta como modelo DS en Tinamit al momento. Si piensas'
                          'que podrías contribuir aquí, ¡contáctenos!').format(ext))
    else:
        errores = {}
        for env in dic_motores[ext]:
            try:
                return env(archivo)
            except BaseException as e:
                errores[env.__name__] = e

        raise ValueError(_('El modelo "{}" no se pudo leer. Intentamos las envolturas siguientes, pero no funcionaron:'
                         '{}').format(''.join(['\n\t{}: {}'.format(env, e) for env, e in errores.items()])))
