import random

from tinamit.BF import ModeloBF


class Envoltura(ModeloBF):

    def ejec(símismo):
        pass

    def incrementar(símismo, paso):

        símismo.variables['Lluvia']['val'] = random.random() * símismo.variables['Bosques']['val']/1000000 * paso

    def leer_vals(símismo):
        pass

    def cambiar_vals_modelo_interno(símismo, valores):
        pass

    def inic_vars(símismo):
        símismo.variables['Lluvia'] = {'val': 1,
                                       'unidades': 'm*m*m/mes',
                                       'ingreso': False,
                                       'egreso': True,
                                       'dims': (1, )
                                       }
        símismo.variables['Bosques'] = {'val': 1000000,
                                        'unidades': 'm*m',
                                        'ingreso': True,
                                        'egreso': False,
                                        'dims': (1, )
                                        }

    def iniciar_modelo(símismo, **kwargs):
        pass

    def obt_unidad_tiempo(símismo):
        return "Meses"

    def cerrar_modelo(símismo):
        pass
