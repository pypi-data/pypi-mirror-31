import os

from tinamit.Conectado import Conectado
from tinamit.Geog.Geog import Lugar, Geografía

from tinamit.Ejemplos.en.Ejemplo_SAHYSMOD.SAHYSMOD import Envoltura


if __name__ == '__main__':
    use_simple = True
    climate_change = True

    # 0. Site geography
    Rechna_Doab = Geografía(nombre='Rechna Doab')

    base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Shape_files')
    Rechna_Doab.agregar_frm_regiones(os.path.join(base_dir, 'Internal_Polygon.shp'), col_orden='Polygon_ID')

    Rechna_Doab.agregar_forma(os.path.join(base_dir, 'External_Polygon.shp'), color='#edf4da')
    Rechna_Doab.agregar_forma(os.path.join(base_dir, 'RIVR.shp'), tipo='agua')
    Rechna_Doab.agregar_forma(os.path.join(base_dir, 'CNL_Arc.shp'), tipo='agua', llenar=False)
    Rechna_Doab.agregar_forma(os.path.join(base_dir, 'Forst_polygon.shp'), tipo='bosque')
    Rechna_Doab.agregar_forma(os.path.join(base_dir, 'buildup_Polygon.shp'), tipo='ciudad')
    Rechna_Doab.agregar_forma(os.path.join(base_dir, 'road.shp'), tipo='calle')

    # 1. Simple runs
    runs_simple = {'CWU': {'Capacity per tubewell': 100.8, 'Fw': 0.8, 'Policy Canal lining': 0,
                           'Policy RH': 0, 'Policy Irrigation improvement': 0},
                   'VD': {'Capacity per tubewell': 153.0, 'Fw': 0.8, 'Policy Canal lining': 0,
                          'Policy RH': 0, 'Policy Irrigation improvement': 0},
                   'CL': {'Capacity per tubewell': 0, 'Fw': 0, 'Policy Canal lining': 1,
                          'Policy RH': 0, 'Policy Irrigation improvement': 0},
                   'RWH': {'Capacity per tubewell': 0, 'Fw': 0, 'Policy Canal lining': 0,
                           'Policy RH': 1, 'Policy Irrigation improvement': 0},
                   'PIM': {'Capacity per tubewell': 0, 'Fw': 0, 'Policy Canal lining': 0,
                           'Policy RH': 0, 'Policy Irrigation improvement': 1}
                   }

    # 2. Complex runs
    # Switch values for runs
    ops = {
        'Capacity per tubewell': [153.0, 100.8],
        'Fw': [0.8, 0],
        'Policy Canal lining': [0, 1],
        'Policy RH': [0, 1],
        'Policy Irrigation improvement': [0, 1]
    }

    runs_complex = {}

    for cp in ops['Capacity per tubewell']:
        for fw in ops['Fw']:
            for cl in ops['Policy Canal lining']:
                for rw in ops['Policy RH']:
                    for ir in ops['Policy Irrigation improvement']:
                        run_name = 'TC {}, Fw {}, CL {}, RW {}, II {}'.format(
                            cp, fw, cl, rw, ir
                        )

                        runs_complex[run_name] = {
                            'Capacity per tubewell': cp,
                            'Fw': fw,
                            'Policy Canal lining': cl,
                            'Policy RH': rw,
                            'Policy Irrigation improvement': ir
                        }

    # 3. Now create the model
    # Create a coupled model instance
    modelo = Conectado()

    # Establish SDM and Biofisical model paths. The Biofisical model path must point to the Python wrapper for the model
    modelo.estab_mds(os.path.join(os.path.split(__file__)[0], 'Vensim', 'Tinamit_sub_v4.vpm'))
    modelo.estab_bf(Envoltura)
    modelo.estab_conv_tiempo(mod_base='mds', conv=6)

    # Couple models(Change variable names as needed)
    modelo.conectar(var_mds='Soil salinity Tinamit CropA', mds_fuente=False, var_bf="CrA - Root zone salinity crop A")
    modelo.conectar(var_mds='Soil salinity Tinamit CropB', mds_fuente=False, var_bf="CrB - Root zone salinity crop B")
    modelo.conectar(var_mds='Area fraction Tinamit CropA', mds_fuente=False,
                    var_bf="Area A - Seasonal fraction area crop A")
    modelo.conectar(var_mds='Area fraction Tinamit CropB', mds_fuente=False,
                    var_bf="Area B - Seasonal fraction area crop B")
    modelo.conectar(var_mds='Watertable depth Tinamit', mds_fuente=False, var_bf="Dw - Groundwater depth")
    modelo.conectar(var_mds='ECdw Tinamit', mds_fuente=False, var_bf='Cqf - Aquifer salinity')
    modelo.conectar(var_mds='Rainfall Tinamit', mds_fuente=False, var_bf='Pp - Rainfall')
    modelo.conectar(var_mds='Lc', mds_fuente=True, var_bf='Lc - Canal percolation')
    modelo.conectar(var_mds='Ia CropA', mds_fuente=True, var_bf='IaA - Crop A field irrigation')
    modelo.conectar(var_mds='Ia CropB', mds_fuente=True, var_bf='IaB - Crop B field irrigation')
    modelo.conectar(var_mds='Gw', mds_fuente=True, var_bf='Gw - Groundwater extraction')
    modelo.conectar(var_mds='EpA', mds_fuente=True, var_bf='EpA - Potential ET crop A')
    modelo.conectar(var_mds='EpB', mds_fuente=True, var_bf='EpB - Potential ET crop B')
    modelo.conectar(var_mds='Irrigation efficiency', mds_fuente=True, var_bf='FsA - Water storage efficiency crop A')
    modelo.conectar(var_mds='Fw', mds_fuente=True, var_bf='Fw - Fraction well water to irrigation')

    # 4. Finally, run the model
    if use_simple:
        runs = runs_simple
    else:
        runs = runs_complex

    if not climate_change:
        # Run the model for all desired runs
        for name, run in runs.items():

            print('Runing model {}.\n-----------------'.format(name))

            # Set appropriate switches for policy analysis
            for switch, val in run.items():
                modelo.mds.inic_val(var=switch, val=val)

            # Simulate the coupled model
            modelo.simular(paso=1, tiempo_final=20, nombre_corrida=name)  # time step and final time are in months

            # Draw maps
            modelo.dibujar_mapa(geog=Rechna_Doab, corrida=name, var='Watertable depth Tinamit', directorio='Maps')
            modelo.dibujar_mapa(geog=Rechna_Doab, corrida=name, var='Soil salinity Tinamit CropA', directorio='Maps')
    else:
        # Climate change runs
        location = Lugar(lat=32.178207, long=73.217391, elev=217)
        location.observar_mensuales('مشاہدہ بارش.csv', meses='مہینہ', años='سال',
                                    cols_datos={'Precipitación': 'بارش (ملیمیٹر)',
                                                'Temperatura mínima': 'درجہ_حرارت_کم',
                                                'Temperatura máxima': 'درجہ_حرارت_زیادہ'
                                                },
                                    conv={'Precipitación': 1,
                                          'Temperatura mínima': 1,
                                          'Temperatura máxima': 1})

        modelo.mds.conectar_var_clima(var='Tmin', var_clima='Temperatura mínima', conv=1)
        modelo.mds.conectar_var_clima(var='Tmax', var_clima='Temperatura máxima', conv=1)
        modelo.estab_conv_meses(6)

        vals_inic = {x: {'mds': v} for x, v in runs.items()}
        dibs = [dict(geog=Rechna_Doab, var='Watertable depth Tinamit', directorio='Maps'),
                dict(geog=Rechna_Doab, var='Soil salinity Tinamit CropA', colores=-1, directorio='Maps')]

        modelo.simular_paralelo(paso=1, tiempo_final=100*2, fecha_inic='01/11/1989', lugar=location, clima=True, recalc=False,
                                tcr=[0, 2.6, 4.5, 6.0, 8.5], vals_inic=vals_inic, combinar=True,
                                nombre_corrida='', dibujar=dibs)
