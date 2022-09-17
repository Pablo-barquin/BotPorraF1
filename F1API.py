import fastf1, os
from fastf1 import api

from FranjaHoraria import TiempoFranjaEspañola

if(os.path.isdir('./Cache')):
    fastf1.Cache.enable_cache('./Cache')

def ObtenerDatosGP(GP):
    
    Datos = {}
    Scarrera = fastf1.get_session(2022, GP, 'R')
    Scarrera.load()

    if(not Scarrera.results.empty):
        Sclasificacion = fastf1.get_session(2022, GP, 'Q')
        Sclasificacion.load()

        Calendario = fastf1.get_event(2022, GP)
        Datos['NombreGP'] = Calendario['Country']
        Datos['Pole'] = Sclasificacion.results.iloc[0].Abbreviation     # Obtenemos la Pole
        Datos['Tiempo Pole'] = Sclasificacion.results.iloc[0].Q3        # Obtenemos tiempo de Pole

        Lista = []
        for i in range(5):
            Lista.append(Scarrera.results.iloc[i].Abbreviation)  # Obtenemos los 5 primeros de la carrera
        Datos['Resultados'] = Lista 

        Fastest_Lap = Scarrera.laps.pick_fastest()
        Datos['VR (Piloto)'] = Fastest_Lap['Driver']    # Vuelta rapida de la carrera
        
        Aux = Scarrera.results.loc[Scarrera.results['Abbreviation'].str.contains("SAI")]    # Puesto de Sainz
        Datos['P-Sainz'] = Aux.iloc[0].Position

        Aux = Scarrera.results.loc[Scarrera.results['Abbreviation'].str.contains("ALO")]    # Puesto de Alonso
        Datos['P-Alonso'] = Aux.iloc[0].Position

        Lista = []
        Weather = api.weather_data(Scarrera.api_path)
        EstadoCircuito = api.track_status_data(Scarrera.api_path)
        
       
        if('4' in EstadoCircuito['Status']):  # Comprobar si ha habido SC en la carrera
            Lista.append('SI')
        else: Lista.append('NO')
        
        if(True in Weather['Rainfall']):    # Comprobar si ha llovido en la carrera
            Lista.append('SI')
        else: Lista.append('NO')

        if('5' in EstadoCircuito['Status']):  # Comprobar si ha habido bandera roja en la carrera
            Lista.append('SI')
        else: Lista.append('NO')
        
        Datos['1Puntos'] = Lista

    return Datos

# Nos permite obtener el horario del GP para ver si la porra esta a tiempo de añadirse
def ObtenerHorariosGP(GP):
    sh = fastf1.get_event(2022, GP) # Obtengo la info del GP
    if(sh.EventFormat == 'conventional'):   # Compruebo si es una carrera Sprint o normal
        return TiempoFranjaEspañola(sh.Location, sh.Session4Date)   # Mando a la funcion la localizacion y hora de clasificacion local
    else:
        return TiempoFranjaEspañola(sh.Location, sh.Session2Date)


# Obtenemos el proximo GP, que tipo es, y los horarios correspondientes
def ObtenerInformacionGP(GP):
    sh = fastf1.get_event(2022, GP) # Obtengo la info del GP
    Nombre = sh.EventName
    if(sh.EventFormat == 'conventional'):
        Tipo = 'Convencional'
        a, b, HorarioClasi = TiempoFranjaEspañola(sh.Location, sh.Session4Date)
    else:
        Tipo = 'Sprint'
        a, b, HorarioClasi = TiempoFranjaEspañola(sh.Location, sh.Session2Date)
    a, b, HorarioCarrera = TiempoFranjaEspañola(sh.Location, sh.Session5Date)

    return Nombre, Tipo, HorarioClasi, HorarioCarrera






# sh = fastf1.get_event_schedule(2021)
# Var = sh.Session4Date
# print(Var.to_pydatetime())
# print(Var.date())

# sh = fastf1.get_session(2022, 1, 'Q')
# sh.load()
# print(sh.results.iloc[0].Q3)


# Calendario = fastf1.get_event_schedule(2022)
# Calendario = Calendario.get_event_by_round(1)
# print(Calendario['Country'])

# sh2 = fastf1.get_session(2022, 1, 'R')
# sh2.load()
# # aux = sh2.results.loc[sh2.results['Abbreviation'].str.contains("SAI")]
# print(sh2['Country'])

# sh2 = fastf1.get_session(2022, 1, 'R')
# sh2.load()
# print(sh.results)

# print(sh.results.iloc[0:10].loc[:, ['Abbreviation', 'Q3']]) # iloc sirve para seleccionar en el indice, y loc sirve para mostrar los datos que yo quiero

# # print(sh.weather_data)

# d = api.weather_data(sh.api_path)
# d2 = api.track_status_data(sh2.api_path)
# print(d["Rainfall"])
# print(d2)

