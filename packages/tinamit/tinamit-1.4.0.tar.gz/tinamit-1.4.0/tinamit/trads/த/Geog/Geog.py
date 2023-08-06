from tinamit.Geog.Geog import Geografía
from tinamit.Geog.Geog import Lugar
from tinamit.Geog.Geog import conv_vars

conv_vars = conv_vars


class Lugar(Lugar):

    def observar_diarios(தன், archivo, cols_datos, c_fecha):
        return super().observar_diarios(archivo=archivo, cols_datos=cols_datos, c_fecha=c_fecha)

    def observar_mensuales(தன், archivo, cols_datos, meses, años):
        return super().observar_mensuales(archivo=archivo, cols_datos=cols_datos, meses=meses, años=años)

    def observar_anuales(தன், archivo, cols_datos, años):
        return super().observar_anuales(archivo=archivo, cols_datos=cols_datos, años=años)

    def prep_datos(தன், ஆரம்பும்_தேதி, fecha_final, tcr, prefs=None, lím_prefs=False, regenerar=False):
        return super().prep_datos(fecha_inic=ஆரம்பும்_தேதி, fecha_final=fecha_final, tcr=tcr, prefs=prefs, lím_prefs=lím_prefs, regenerar=regenerar)

    def devolver_datos(தன், vars_clima, f_inic, f_final):
        return super().devolver_datos(vars_clima=vars_clima, f_inic=f_inic, f_final=f_final)

    def comb_datos(தன், vars_clima, combin, f_inic, f_final):
        return super().comb_datos(vars_clima=vars_clima, combin=combin, f_inic=f_inic, f_final=f_final)


class Geografía(Geografía):

    def agregar_objeto(தன், archivo, nombre=None, tipo=None, alpha=None, color=None, llenar=None):
        return super().agregar_objeto(archivo=archivo, nombre=nombre, tipo=tipo, alpha=alpha, color=color, llenar=llenar)

    def agregar_regiones(தன், archivo, col_orden=None):
        return super().agregar_regiones(archivo=archivo, col_orden=col_orden)

    def dibujar(தன், archivo, valores=None, título=None, unidades=None, colores=None, escala=None):
        return super().dibujar(archivo=archivo, valores=valores, título=título, unidades=unidades, colores=colores, escala=escala)
