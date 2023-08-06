import ctypes
import os
import re
import csv

import numpy as np

from tinamit import _
from tinamit.Modelo import Modelo


class EnvolturaMDS(Modelo):
    """
    Esta clase sirve para representar modelo de dinámicas de los sistemas (EnvolturaMDS). Se debe crear una subclase para cada
    tipo de EnvolturaMDS. Al momento, el único incluido es VENSIM.
    """

    ext_arch_egr = '.csv'

    def __init__(símismo, archivo):
        """
        Iniciamos el modelo DS.

        :param archivo: El archivo con el modelo DS.
        :type archivo: str
        """

        # Listas vacías para distintos tipos de variables.
        símismo.constantes = []
        símismo.niveles = []
        símismo.flujos = []
        símismo.auxiliares = []
        símismo.internos = []  # variables internos al EnvolturaMDS (p. ej., TIMESTEP y TIME en Vensim)

        # Un diccionario con un poco de información adicional sobre los variables. Debe tener las llaves "hijos",
        # "parientes" y "ec".

        símismo.dic_info_vars = {}

        # Acordarse de dónde venimos
        símismo.archivo = archivo

        # Modelos DS se identifican por el nombre 'mds'.
        super().__init__(nombre='mds')

    def inic_vars(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturaMDS.EnvolturaMDS` para implementar. Además de
        los diccionarios de variables normales, debe establecer `símismo.constantes`, `símismo.flujos`,
        `símismo.niveles`, `símismo.editables`, `símismo.auxiliares`, y `símismo.dic_info_vars`. Este último
        debe tener las llaves "hijos", "parientes" y "ec".

        Ver :func:`Modelo.Modelo.inic_vars` para más información.
        """

        raise NotImplementedError

    def obt_unidad_tiempo(símismo):
        """
        Cada envoltura de programa DS debe implementar este metodo para devolver las unidades de tiempo del modelo DS
        cargado.

        :return: Las unidades del modelo DS cargado.
        :rtype: str

        """
        raise NotImplementedError

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturaMDS.EnvolturaMDS` para implementar. Notar que la
        implementación de este método debe incluir la aplicación de valores iniciales.

        Ver :func:`Modelo.Modelo.iniciar_modelo` para más información.

        :param nombre_corrida: El nombre de la corrida (útil para guardar resultados).
        :type nombre_corrida: str

        :param tiempo_final: El tiempo final de la simulación.
        :type tiempo_final: int

        """
        raise NotImplementedError

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturaMDS.EnvolturaMDS` para implementar.

        Ver :func:`Modelo.Modelo.cambiar_vals_modelo` para más información.

        :param valores: El diccionario de valores para cambiar.
        :type valores: dict

        """
        raise NotImplementedError

    def incrementar(símismo, paso):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturaMDS.EnvolturaMDS` para implementar.

        Debe avanzar la simulación del modelo DS de ``paso`` unidades de tiempo.  Ver
        :func:`Modelo.Modelo.incrementar` para más información.

        :param paso: El paso con cual incrementar el modelo.
        :type paso: int

        """
        raise NotImplementedError

    def leer_vals(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturaMDS.EnvolturaMDS` para implementar.

        Debe leer los valores de los variables en el modelo EnvolturaMDS. Si es más fácil, puede simplemente leer los valores
        de los variables que están en la lista ``EnvolturaMDS.vars_saliendo`` (los variables del DS que están
        conectados con el modelo biofísico).

        Ver :func:`Modelo.Modelo.leer_vals` para más información.

        """
        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturaMDS.EnvolturaMDS` para implementar.

        Debe llamar acciones necesarias para terminar la simulación y cerrar el modelo DS, si aplican.

        Ver :func:`Modelo.Modelo.cerrar_modelo` para más información.

        """
        raise NotImplementedError

    def leer_resultados_mds(símismo, corrida, var):
        """
        Esta función lee los resultados desde un archivo de egresos del modelo DS.

        :param corrida: El nombre de la corrida. Debe corresponder al nombre del archivo de egresos.
        :type corrida: str
        :param var: El variable de interés.
        :type var: str
        :return: Una matriz de los valores del variable de interés.
        :rtype: np.ndarray
        """

        if var not in símismo.variables:
            raise ValueError(_('El variable "{}" no existe.').format(var))

        if os.path.splitdrive(corrida)[0] == '':
            archivo = os.path.join(os.path.split(símismo.archivo)[0], corrida)
        else:
            archivo = corrida

        archivo += símismo.ext_arch_egr

        return leer_egr_mds(archivo, var)

    def __getinitargs__(símismo):

        return símismo.archivo,


class MDSEditable(EnvolturaMDS):
    pass


def leer_egr_mds(archivo, var, saltar_última=True):
    """
    Lee archivos de egresos de simulaciones EnvolturaMDS.

    :param archivo: El archivo de egresos.
    :type archivo: str
    :param var: El variable de interés
    :type var: str
    :return: Una matriz con los valores del variable de interés.
    :rtype: np.ndarray
    """

    ext = os.path.splitext(archivo)[1]
    if ext == '':
        ext = '.vdf'
        archivo += ext

    datos = []
    final = None

    if ext == '.vdf':
        ext = '.csv'
        archivo_csv = os.path.split(archivo)[1].replace('.vdf', '.csv')

        dll_vensim = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')

        dll_vensim.vensim_command('MENU>VDF2CSV|{vdffile}|{CSVfile}'
                       .format(vdffile=archivo, CSVfile=archivo_csv).encode())

        archivo = archivo.replace('.vdf', '.csv')
        if saltar_última:
            final = -1

    if ext == '.csv':

        with open(archivo) as d:
            lector = csv.reader(d)
            filas = [f for f in lector if re.match('{}(\[.*\])?$'.format(var), f[0])]

        for f in filas:
            datos.append(f[1:])

    else:
        raise ValueError(_('El formato de datos "{}" no se puede leer al momento.').format(ext))

    return np.array(datos, dtype=float)[..., :final]
