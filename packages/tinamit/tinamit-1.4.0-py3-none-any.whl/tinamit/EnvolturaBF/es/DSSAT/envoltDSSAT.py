from tinamit.BF import ModeloFlexible


class ModeloDSSAT(ModeloFlexible):

    def __init__(símismo, exe_DSSAT, archivo_ingr):
        super().__init__()

        args = {'exe_DSSAT': exe_DSSAT, 'archivo_ingr': archivo_ingr}
        símismo.comanda = '{exe_DSSAT} B {archivo_ingr}'.format(**args)

        símismo.día_act = 0  # El día actual de la simulación
        símismo.día_princ_últ_sim = 0  # El primer día de la última llamada a DSSAT

    def iniciar_modelo(símismo, tiempo_final, **kwargs):

        símismo.inic_vars_clima(tiempo_final=tiempo_final)

    def cerrar_modelo(símismo):
        pass  # Aquí no hay nada que hacer.

    def inic_vars(símismo):

        símismo.variables.clear()

        for name, dic in vars_DSSAT.items():
            símismo.variables[name] = {'val': None,
                                       'unidades': dic['unidades'],
                                       'ingreso': dic['ingr'],
                                       'egreso': dic['egr'],
                                       'dims': (1,)
                                       }

    def obt_unidad_tiempo(símismo):
        return 'Días'

    def leer_vals(símismo):

        for var in símismo.vars_saliendo:
            raise NotImplementedError

    def incrementar(símismo, paso):
        raise NotImplementedError

    def cambiar_vals_modelo_interno(símismo, valores):
        raise NotImplementedError

    def mandar_simul(símismo):
        raise NotImplementedError

    def inic_vars_clima(símismo, tiempo_final):
        raise NotImplementedError

vars_DSSAT = {
    'Rendimiento': {
        'Código': None,
        'Archivo': None,
        'Sección': None,
        'Unidades': 'kg/ha',
        'ingr': False,
        'egr': True
    }
}