import csv
import datetime as ft
import os

import matplotlib.colors as colors
import numpy as np
import pandas as pd
import shapefile as sf
from matplotlib import cm
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura

from taqdir.ذرائع.مشاہدات import دن_مشا, مہنہ_مشا, سال_مشا
from taqdir.مقام import مقام
from tinamit import _

# Ofrecemos la oportunidad de utilizar تقدیر, taqdir, en español

conv_vars = {
    'Precipitación': 'بارش',
    'Radiación solar': 'شمسی_تابکاری',
    'Temperatura máxima': 'درجہ_حرارت_زیادہ',
    'Temperatura mínima': 'درجہ_حرارت_کم',
    'Temperatura promedia': 'درجہ_حرارت_اوسط'
}


# Una subclase traducida
class Lugar(مقام):
    """
    Esta clase conecta con la clase مقام, o Lugar, del paquete taqdir.
    """

    def __init__(símismo, lat, long, elev):
        """
        Inciamos el :class:`Lugar` con sus coordenadas.

        :param lat: La latitud del lugares.
        :type lat: float | int
        :param long: La longitud del lugares.
        :type long: float | int
        :param elev: La elevación del lugares, en metros.
        :type elev: float | int
        """

        # Iniciamos como مقام
        super().__init__(چوڑائی=lat, طول=long, بلندی=elev)

    def observar_diarios(símismo, archivo, cols_datos, conv, c_fecha):
        """
        Esta función permite conectar observaciones diarias de datos climáticos.

        :param archivo: El archivo con la base de datos.
        :type archivo: str

        :param cols_datos: Un diccionario, donde cada llave es el nombre oficial del variable climático y
          el valor es el nombre de la columna en la base de datos.
        :type cols_datos: dict[str, str]

        :param conv: Diccionario de factores de conversión para cada variable. Las llaves deben ser el nombre del
          variable **en Tinamït**.
        :type conv: dict[str, int | float]

        :param c_fecha: El nombre de la columna con las fechas de las observaciones.
        :type c_fecha: str

        """

        for v in cols_datos:
            if v not in conv_vars:
                raise KeyError(_('Error en observaciones diarias: "{}" no es variable climático reconocido en Tinamït. '
                                 'Debe ser uno de: {}').format(v, ', '.join(conv_vars)))
        for v in conv:
            if v not in conv_vars:
                raise KeyError(_('Error en factores de conversión: "{}" no es variable climático reconocido en '
                                 'Tinamït. Debe ser uno de: {}').format(v, ', '.join(conv_vars)))

        d_cols = {conv_vars[x]: cols_datos[x] for x in cols_datos}
        d_conv = {conv_vars[v]: c for v, c in conv.items()}

        obs = دن_مشا(مسل=archivo, تبادلوں=d_conv, س_تاریخ=c_fecha, س_اعداد=d_cols)

        símismo.مشاہدہ_کرنا(مشاہد=obs)

    def observar_mensuales(símismo, archivo, cols_datos, conv, meses, años):
        """
        Esta función permite conectar observaciones mensuales de datos climáticos.

        :param archivo: El archivo con la base de datos.
        :type archivo: str

        :param cols_datos: Un diccionario, donde cada llave es el nombre oficial del variable climático y el valor es
          el nombre de la columna en la base de datos.
        :type cols_datos: dict[str, str]

        :param conv: Diccionario de factores de conversión para cada variable. Las llaves deben ser el nombre del
          variable **en Tinamït**.
        :type conv: dict[str, int | float]

        :param meses: El nombre de la columna con los meses de las observaciones.
        :type meses: str

        :param años: El nombre de la columna con los años de las observaciones.
        :type años: str

        """

        for v in cols_datos:
            if v not in conv_vars:
                raise KeyError(_('Error en observaciones mensuales: "{}" no es variable climático reconocido en '
                                 'Tinamït. Debe ser uno de: {}').format(v, ', '.join(conv_vars)))
        for v in conv:
            if v not in conv_vars:
                raise KeyError(_('Error en factores de conversión: "{}" no es variable climático reconocido en '
                                 'Tinamït. Debe ser uno de:\t\n{}').format(v, ', '.join(conv_vars)))

        d_cols = {conv_vars[x]: cols_datos[x] for x in cols_datos}
        d_conv = {conv_vars[v]: c for v, c in conv.items()}

        obs = مہنہ_مشا(مسل=archivo, س_اعداد=d_cols, تبادلوں=d_conv, س_مہینہ=meses, س_سال=años)

        símismo.مشاہدہ_کرنا(obs)

    def observar_anuales(símismo, archivo, cols_datos, conv, años):
        """
        Esta función permite conectar observaciones anuales de datos climáticos.

        :param archivo: El archivo con la base de datos.
        :type archivo: str

        :param cols_datos: Un diccionario, donde cada llave es el nombre oficial del variable climático y el valor es
          el nombre de la columna en la base de datos.
        :type cols_datos: dict[str, str]

        :param conv: Diccionario de factores de conversión para cada variable. Las llaves deben ser el nombre del
          variable **en Tinamït**.
        :type conv: dict[str, int | float]

        :param años: El nombre de la columna con los años de las observaciones.
        :type años: str

        """

        for v in cols_datos:
            if v not in conv_vars:
                raise KeyError(_('Error en observaciones anuales: "{}" no es variable climático reconocido en Tinamït. '
                                 'Debe ser uno de: {}').format(v, ', '.join(conv_vars)))
        for v in conv:
            if v not in conv_vars:
                raise KeyError(_('Error en factores de conversión: "{}" no es variable climático reconocido en '
                                 'Tinamït. Debe ser uno de: {}').format(v, ', '.join(conv_vars)))

        d_cols = {conv_vars[x]: cols_datos[x] for x in cols_datos}
        d_conv = {conv_vars[v]: c for v, c in conv.items()}

        obs = سال_مشا(مسل=archivo, س_اعداد=d_cols, تبادلوں=d_conv, س_سال=años)
        símismo.مشاہدہ_کرنا(obs)

    def prep_datos(símismo, fecha_inic, fecha_final, tcr, prefs=None, lím_prefs=False, regenerar=False):
        """
        Esta función actualiza el diccionario interno de datos climáticos del Lugar, listo para una simulación.
        Intentará obtener datos de todas fuentes posibles, incluso observaciones y modelos de predicciones climáticas.

        :param fecha_inic: La fecha inicial.
        :type fecha_inic: ft.date | ft.datetime
        :param fecha_final: La fecha final.
        :type fecha_final: ft.date | ft.datetime
        :param tcr: El escenario climático, o trayectorio de concentración relativa (tcr), de la IPCC
          (puede ser uno de 2.6, 4.5, 6.0, o 8.5).
        :type tcr: str | float
        :param prefs: Una lista opcional de fuentes potenciales de datos, en orden de preferencia.
        :type prefs: list
        :param lím_prefs: Si hay que limitar las fuentes de datos
        :type lím_prefs: bool
        :param regenerar: Si hay que regenerar datos o no.
        :type regenerar: bool

        """
        super().اعداد_تیاری(fecha_inic, fecha_final, tcr, ش_ترکار=1, ترجیحات=prefs, ترجیحات_محدود=lím_prefs,
                            دوبارہ_پیدا=regenerar)

    def devolver_datos(símismo, vars_clima, f_inic, f_final):
        """
        Esta función devuelve datos ya calculados por :func:`~tinamit.Geog.Geog.Lugar.prep_datos`.

        :param vars_clima: Una lista de variables climáticos de interés.
        :type vars_clima: list[str]
        :param f_inic: La fecha inicial.
        :type f_inic: ft.datetime | ft.date
        :param f_final: La fecha final.
        :type f_final: ft.datetime | ft.date
        :return: Los datos pedidos.
        :rtype: pd.DataFrame
        """
        bd = símismo.اعداد_دن  # type: pd.DataFrame
        datos_interés = bd.loc[f_inic:f_final]

        for v in vars_clima:
            if v not in conv_vars:
                raise ValueError(_('El variable "{}" está erróneo. Debe ser uno de:\n'
                                 '\t{}').format(v, ', '.join(conv_vars)))

        v_conv = [conv_vars[v] for v in vars_clima]

        return datos_interés[v_conv]

    def comb_datos(símismo, vars_clima, combin, f_inic, f_final):
        """
        Esta función combina datos climáticos entre dos fechas.

        :param vars_clima: Los variables de clima de interés.
        :type vars_clima: list[str]
        :param combin: Cómo hay que combinar (promedio o total)
        :type combin: list[str]
        :param f_inic: La fecha inicial
        :type f_inic: ft.datetime | ft.date
        :param f_final: La fecha final
        :type f_final: ft.datetime | ft.date
        :return: Un diccionario con los resultados.
        :rtype: dict[np.ndarray]
        """

        bd = símismo.اعداد_دن  # type: pd.DataFrame
        datos_interés = bd.loc[f_inic:f_final]

        resultados = {}
        for v, c in zip(vars_clima, combin):
            try:
                v_conv = conv_vars[v]
            except KeyError:
                raise ValueError(_('El variable "{}" está erróneo. Debe ser uno de:\n'
                                 '\t{}').format(v, ', '.join(conv_vars)))
            if c is None:
                if v in ['Temperatura máxima', 'Temperatura mínima', 'Temperatura promedia']:
                    c = 'prom'
                else:
                    c = 'total'

            if c == 'prom':
                resultados[v] = datos_interés[v_conv].mean()
            elif c == 'total':
                resultados[v] = datos_interés[v_conv].sum()
            else:
                raise ValueError

        return resultados


class Geografía(object):
    """
    Esta clase representa la geografía de un lugares.
    """
    def __init__(símismo, nombre):

        símismo.nombre = nombre
        símismo.regiones = {}
        símismo.objetos = {}

        símismo.orden_esc_geog = None
        símismo.árbol_geog = {}
        símismo.árbol_geog_inv = {}
        símismo.cód_a_lugar = {}
        símismo.grupos = []
        símismo.orden_jer = []

    def agregar_forma(símismo, archivo, nombre=None, tipo=None, alpha=None, color=None, llenar=None):
        if nombre is None:
            nombre = os.path.splitext(os.path.split(archivo)[1])[0]

        símismo.objetos[nombre] = {'obj': sf.Reader(archivo),
                                   'color': color,
                                   'llenar': llenar,
                                   'alpha': alpha,
                                   'tipo': tipo}

    def agregar_frm_regiones(símismo, archivo, col_id=None, col_orden=None, escala_geog=None):
        """

        :param archivo:
        :type archivo:
        :param col_id:
        :type col_id:
        :param col_orden:
        :type col_orden:
        :return:
        :rtype:
        """

        if escala_geog is None:
            escala_geog = 'Principal'

        af = sf.Reader(archivo)

        attrs = af.fields[1:]
        nombres_attr = [field[0] for field in attrs]

        if col_orden is not None:
            try:
                orden = np.array([x.record[nombres_attr.index(col_orden)] for x in af.shapeRecords()])
            except ValueError:
                raise ValueError(_('La columna "{}" no existe en la base de datos.').format(col_orden))

            orden -= np.min(orden)

        else:
            orden = range(len(af.records()))

        if col_id is not None:
            try:
                ids = np.array([x.record[nombres_attr.index(col_orden)] for x in af.shapeRecords()])
            except ValueError:
                raise ValueError(_('La columna "{}" no existe en la base de datos.').format(col_orden))
        else:
            ids = None

        símismo.regiones[escala_geog] = {'af': af, 'orden_regs': orden, 'id': ids}

    def agregar_info_regiones(símismo, archivo, col_cód, orden_jer=None, grupos=None):
        """

        :param archivo:
        :type archivo:
        :param orden_jer:
        :type orden_jer:
        :param col_cód:
        :type col_cód:
        """

        símismo.orden_jer = orden_jer

        símismo.leer_archivo_info_reg(archivo=archivo, orden_jer=orden_jer, col_cód=col_cód, grupos=grupos)

    def leer_archivo_info_reg(símismo, archivo, orden_jer, col_cód, grupos=None):

        símismo.árbol_geog.clear()
        símismo.árbol_geog_inv.clear()
        símismo.grupos.clear()

        if grupos is None:
            grupos = []
        if not isinstance(grupos, list):
            grupos = [grupos]

        with open(archivo, newline='') as d:

            l = csv.reader(d)  # El lector de csv

            # Guardar la primera fila como nombres de columnas
            cols = next(l)

            try:
                i_cols = [cols.index(x) for x in orden_jer]
            except ValueError:
                raise ValueError(_('Los nombres de las regiones en "orden_jer" ({}) no concuerdan con los nombres en el'
                                 ' archivo ({}).').format(', '.join(orden_jer), ', '.join(cols)))
            try:
                in_col_cód = cols.index(col_cód)
            except ValueError:
                raise ValueError(_('La columna de código de región especificada ({}) no concuerda con los nombres de '
                                 'columnas del archivo ({}).').format(col_cód, ', '.join(cols)))

            try:
                í_g = [cols.index(x) for x in grupos]
                símismo.grupos.extend(grupos)
            except ValueError:
                raise ValueError(_('Una o más de las columnas de grupo especificadas ({}) no concuerda con los nombres '
                                   'de columnas del archivo ({}).').format(grupos, ', '.join(cols)))

            # Para cada fila que sigue en el csv...
            for f in l:
                dic = símismo.árbol_geog
                cód = f[in_col_cód]

                for í, n in enumerate(i_cols):

                    if í == len(i_cols) - 1:
                        dic[f[n]] = cód

                    elif f[n] not in dic:
                        dic[f[n]] = {}

                    dic = dic[f[n]]

                símismo.árbol_geog_inv[cód] = dict([(orden_jer[k], f[j]) for k, j in enumerate(i_cols)])

                for í, g in zip(í_g, grupos):
                    nmb_gp = f[í]
                    if len(nmb_gp):
                        símismo.árbol_geog_inv[cód][g] = nmb_gp
                    else:
                        símismo.árbol_geog_inv[cód][g] = None

                escala = orden_jer[max([n for n, i in enumerate(i_cols) if f[i] != ''])]
                nombre = f[cols.index(escala)]
                símismo.cód_a_lugar[cód] = {'escala': escala, 'nombre': nombre}

    def obt_lugares_en(símismo, escala=None, en=None, por=None):
        """"""

        if escala is None:
            escala = símismo.orden_jer[-1]
        if en is None:
            regiones = [x for x, d in símismo.árbol_geog_inv.items() if símismo.cód_a_lugar[x]['escala'] == escala]
        else:
            if isinstance(en, dict):
                # Grupos
                escala_en = list(en)[0]
                nombres_en = en[escala_en]
                if not isinstance(nombres_en, list):
                    nombres_en = [nombres_en]
            else:
                if not isinstance(en, list):
                    en = [en]
                escala_en = símismo.cód_a_lugar[en[0]]['escala']
                if not all(símismo.cód_a_lugar[x]['escala'] == escala_en for x in en):
                    raise ValueError('')

                nombres_en = [símismo.cód_a_lugar[x]['nombre'] for x in en]

            nombres_en = [str(x) for x in nombres_en]
            regiones = [x for x, d in símismo.árbol_geog_inv.items() if d[escala_en] in nombres_en and
                        símismo.cód_a_lugar[x]['escala'] == escala]

        if por is None:
            return regiones
        else:
            categs = {}
            for r in regiones:
                try:
                    cat = símismo.árbol_geog_inv[r][por]
                    if por in símismo.grupos:
                        if cat is not None:
                            cat = '{} {}'.format(por, cat)
                        else:
                            cat = None
                except KeyError:
                    cat = None

                if cat is not None:
                    if cat in categs:
                        categs[cat].append(r)
                    else:
                        categs[cat] = [r]

            return categs

    def obt_en_grupo(símismo, tipo_grupo, grupos):

        if not isinstance(grupos, list) and not isinstance(grupos, tuple) and not isinstance(grupos, set):
            grupos = [grupos]
        grupos = [str(x) for x in grupos]

        if tipo_grupo not in símismo.grupos:
            raise ValueError('')

        return [x for x, d in símismo.árbol_geog_inv.items() if str(d[tipo_grupo]) in grupos]

    def dibujar(símismo, archivo, valores=None, título=None, unidades=None, colores=None, escala_num=None):
        """
        Dibuja la Geografía.

        :param archivo: Dónde hay que guardar el mapa.
        :type archivo: str
        :param valores: Los valores para dibujar.
        :type valores: np.ndarray
        :param título: El título del mapa.
        :type título: str
        :param unidades: Las unidades de los valores.
        :type unidades: str
        :param colores: Los colores para dibujar.
        :type colores: str | list | tuple | int
        :param escala_num: La escala numérica para los colores.
        :type escala_num: tuple

        """

        if colores is None:
            colores = ['#FF6666', '#FFCC66', '#00CC66']
        if colores == -1:
            colores = ['#00CC66', '#FFCC66','#FF6666']

        if isinstance(colores, str):
            colores = ['#FFFFFF', colores]
        elif isinstance(colores, tuple):
            colores = list(colores)

        fig = Figura()
        TelaFigura(fig)
        ejes = fig.add_subplot(111)
        ejes.set_aspect('equal')

        if valores is not None:
            d_regiones = None
            for escala, d_reg in símismo.regiones.items():
                if len(d_reg['orden_regs']) == valores.shape[0]:
                    d_regiones = d_reg
                    continue

            if d_regiones is None:
                raise ValueError(_('El número de regiones en los datos no concuerdan con la geografía del lugar.'))

            regiones = d_regiones['af']
            orden = d_regiones['orden_regs']

            n_regiones = len(regiones.shapes())
            if len(valores) != n_regiones:
                raise ValueError(_('El número de regiones no corresponde con el tamñao de los valores.'))

            if escala_num is None:
                escala_num = (np.min(valores), np.max(valores))
            if len(escala_num) != 2:
                raise ValueError

            vals_norm = (valores - escala_num[0]) / (escala_num[1] - escala_num[0])

            d_clrs = _gen_d_mapacolores(colores=colores)

            mapa_color = colors.LinearSegmentedColormap('mapa_color', d_clrs)
            norm = colors.Normalize(vmin=escala_num[0], vmax=escala_num[1])
            cpick = cm.ScalarMappable(norm=norm, cmap=mapa_color)
            cpick.set_array([])

            v_cols = mapa_color(vals_norm)
            _dibujar_shp(ejes=ejes, frm=regiones, orden=orden, colores=v_cols)

            if unidades is not None:
                fig.colorbar(cpick, label=unidades)
            else:
                fig.colorbar(cpick)

        for nombre, d_obj in símismo.objetos.items():

            tipo = d_obj['tipo']

            for a in ['color', 'llenar', 'alpha']:
                if d_obj[a] is None:
                    d_obj[a] = _formatos_auto(a, tipo)

            color = d_obj['color']
            llenar = d_obj['llenar']
            alpha = d_obj['alpha']

            _dibujar_shp(ejes=ejes, frm=d_obj['obj'], colores=color, alpha=alpha, llenar=llenar)

        if título is not None:
            ejes.set_title(título)

        fig.savefig(archivo, dpi=500)

    def __str__(símismo):
        return símismo.nombre


def _dibujar_shp(ejes, frm, colores, orden=None, alpha=1.0, llenar=True):
    """
    Dibujar una forma geográfica.

    Basado en código de Chris Halvin: https://github.com/chrishavlin/learning_shapefiles/tree/master/src

    :param ejes: Los ejes de Matplotlib.
    :type ejes: matplotlib.axes._subplots.Axes

    :param frm: La forma.
    :type frm: sf.Reader

    :param colores: Los colores para dibujar.
    :type colores: str | list[str] | np.ndarray

    :param orden: El orden de las partes de la forma, relativo al orden de las colores.
    :type orden: np.ndarray | list

    :param alpha: La transparencia
    :type alpha: float | int

    :param llenar: Si hay que llenar la forma, o simplemente dibujar los contornos.
    :type llenar: bool
    """

    n_formas = len(frm.shapes())

    if orden is not None:
        regiones = [x for _, x in sorted(zip(orden, frm.shapes()))]
    else:
        regiones = frm.shapes()

    if isinstance(colores, str) or isinstance(colores, tuple):
        colores = [colores] * n_formas
    else:
        if len(colores) != n_formas:
            raise ValueError

    for forma, col in zip(regiones, colores):
        n_puntos = len(forma.points)
        n_partes = len(forma.parts)

        if n_partes == 1:
            x_lon = np.zeros((len(forma.points), 1))
            y_lat = np.zeros((len(forma.points), 1))
            for ip in range(len(forma.points)):
                x_lon[ip] = forma.points[ip][0]
                y_lat[ip] = forma.points[ip][1]
            if llenar:
                ejes.fill(x_lon, y_lat, color=col, alpha=alpha)
            else:
                ejes.plot(x_lon, y_lat, color=col, alpha=alpha)

        else:
            for ip in range(n_partes):  # Para cada parte del imagen
                i0 = forma.parts[ip]
                if ip < n_partes - 1:
                    i1 = forma.parts[ip + 1] - 1
                else:
                    i1 = n_puntos

                seg = forma.points[i0:i1 + 1]
                x_lon = np.zeros((len(seg), 1))
                y_lat = np.zeros((len(seg), 1))
                for i in range(len(seg)):
                    x_lon[i] = seg[i][0]
                    y_lat[i] = seg[i][1]

                if llenar:
                    ejes.fill(x_lon, y_lat, color=col, alpha=alpha)
                else:
                    ejes.plot(x_lon, y_lat, color=col, alpha=alpha)


def _hex_a_rva(hx):
    """
    Convierte colores RVA a Hex.

    :param hx: El valor hex.
    :type hx: str
    :return: El valor rva.
    :rtype: tuple
    """
    return tuple(int(hx.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))


def _gen_d_mapacolores(colores):
    """
    Genera un diccionario de mapa de color para MatPlotLib.

    :param colores: Una lista de colores
    :type colores: list
    :return: Un diccionario para MatPlotLib
    :rtype: dict
    """

    clrs_rva = [_hex_a_rva(x) for x in colores]
    n_colores = len(colores)

    dic_c = {'red': tuple((round(i / (n_colores - 1), 2), clrs_rva[i][0] / 255, clrs_rva[i][0] / 255) for i in
                          range(0, n_colores)),
             'green': tuple(
                 (round(i / (n_colores - 1), 2), clrs_rva[i][1] / 255, clrs_rva[i][1] / 255) for i in
                 range(0, n_colores)),
             'blue': tuple(
                 (round(i / (n_colores - 1), 2), clrs_rva[i][2] / 255, clrs_rva[i][2] / 255) for i in
                 range(0, n_colores))}

    return dic_c


def _formatos_auto(a, tipo):
    """
    Formatos automáticos para objetos en mapas.

    :param a: El atributo.
    :type a: str
    :param tipo: El tipo de objeto geográfico.
    :type tipo: str
    :return: El atributo automático.
    :rtype: str | bool | float
    """

    d_formatos = {
        'agua': {'color': '#A5BFDD',
                 'llenar': True,
                 'alpha': 0.5},
        'calle': {'color': '#7B7B7B',
                  'llenar': False,
                  'alpha': 1.0},
        'ciudad': {'color': '#FB9A99',
                   'llenar': True,
                   'alpha': 1.0},
        'bosque': {'color': '#33A02C',
                   'llenar': True,
                   'alpha': 0.7},
        'otro': {'color': '#FFECB3',
                 'llenar': False,
                 'alpha': 1.0}
    }

    if tipo is None or tipo not in d_formatos:
        tipo = 'otro'

    return d_formatos[tipo.lower()][a.lower()]
