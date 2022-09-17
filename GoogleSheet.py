import gspread, ast

from oauth2client.service_account import ServiceAccountCredentials 
from datetime import datetime, timedelta

from F1API import ObtenerDatosGP

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', 
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"] 
  
Credenciales = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope) 
Cliente = gspread.authorize(Credenciales) 
Hoja = Cliente.open("Porra F1 BOT")

Puntuaciones = Hoja.get_worksheet(1)        # Hoja Porra_2022
Datos = Hoja.get_worksheet(2)               # Hoja Porras_Actuales
PorrasAnteriores = Hoja.get_worksheet(3)    # Hoja Porras_Anteriores

GP = int(Puntuaciones.acell('A28').value)   # GP en el que nos encontramos

# Obtenemos el token privado para editar nuestro BOT
def ObtenerTokenBot():
    return str(Puntuaciones.acell('A29').value)

# Guarda los datos de la nueva porra.
def GuardadoDatos(BaseDatos):

    # Selecciono el rango de valores a cambiar
    cell_list = Datos.range('B2:E8')

    # Actualizo las celdas con los valores que se encuentren actualmente en la base de datos
    z = k = 0
    for i in BaseDatos:
        for j in BaseDatos[i]:
            if j != 'Codigo':
                cell_list[z+k*4].value = str(BaseDatos[i][j])
                k += 1
        z += 1
        k = 0

    # Cargo los nuevos datos
    Datos.update_cells(cell_list)

    # Actualizo los códigos que nos permiten modificar las porras
    Datos.update('H100:K100', [[BaseDatos['PABLO']['Codigo'], BaseDatos['JOSEMA']['Codigo'], BaseDatos['RAUL']['Codigo'], BaseDatos['MIGUEL']['Codigo']]])

# Cargamos las porras que existen ahora mismo para la carrera actual
def CargaDatos(BaseDatos):
    z = k = 0
    for i in BaseDatos:
        BaseDatos[i] = dict.fromkeys(['Pole', 'Tiempo Pole', 'Resultados', 'VR (Piloto)', 'P-Sainz', 'P-Alonso', '1Puntos', 'Codigo'], None)
        Celdas = Datos.col_values(2+k)
        for j in BaseDatos[i]:
            if j != 'Codigo':
                BaseDatos[i][j] = Celdas[z+1]
                z = z+1
        BaseDatos[i]["Resultados"] = BaseDatos[i]["Resultados"].strip("][").replace("\'", '').split(', ')
        BaseDatos[i]["1Puntos"] = BaseDatos[i]["1Puntos"].strip("][").replace("\'", '').split(', ')
        z = 0
        k += 1
    
    # Cargo los códigos que hayan para modificar las porras
    z = 0
    Codigos = Datos.get_values('H100:K100')
    for i in BaseDatos:
        BaseDatos[i]['Codigo'] = Codigos[0][z]
        z += 1

# Realizamos la actualizacion de puntos de la porra
def ActualizacionPuntos(BaseDatos):
    global GP
    DatosGP = ObtenerDatosGP(GP)    # Vamos a obtener primero los datos de los puntos actuales

    if DatosGP: # Si no tenemos datos, significa que la carrera todavia no ha ocurrido o la API no ha cargado los datos
        Valor = []
        Tiempos = []
        for j in BaseDatos: # Por cada usuario de la base de datos, compruebo los puntos que ha obtenido
            Valor.append(CalculoPuntos(BaseDatos[j], DatosGP))
            Tiempos.append(abs(TransformacionTiempo(BaseDatos[j]['Tiempo Pole']) - DatosGP['Tiempo Pole'])) # Saco la diferencia del tiempo del usuario con la pole de la carrera

        if(min(Tiempos) < timedelta(days=0, hours=0, minutes=0, seconds=0, microseconds=500000)):  
            Valor[Tiempos.index(min(Tiempos))] += 5     # El usuario con el tiempo mas cercano, se le suma los puntos
        Puntuaciones.update(f'A{GP+1}:E{GP+1}', [[DatosGP['NombreGP'], Valor[0], Valor[1], Valor[2], Valor[3]]])    # Cargamos la base de datos de Google
        LimpiarBaseDatos(BaseDatos, DatosGP)     # Despues de contar los puntos, limpio la porra para preparase para la siguiente carrera
        GP += 1
        Puntuaciones.update_acell('A28', GP)

    PuntosActuales = Puntuaciones.row_values(26)
    return PuntosActuales

# Obtenemos los puntos del usuario a la carrera, sin sumar los puntos de tiempo
def CalculoPuntos(Usuario, Datos):
    Valor = 0
    
    # Sumo todos los aciertos que sean de 3 puntos
    if(Usuario["Pole"] == Datos["Pole"]): Valor += 3
    if(Usuario["VR (Piloto)"] == Datos["VR (Piloto)"]): Valor += 3

    if(Usuario['P-Sainz'] != 'None' and Usuario['P-Sainz'] != 'NONE'):
        if(int(Usuario["P-Sainz"]) == Datos["P-Sainz"]): Valor += 3
    
    if(Usuario['P-Alonso'] != 'None' and Usuario['P-Alonso'] != 'NONE'):
        if(int(Usuario["P-Alonso"]) == Datos["P-Alonso"]): Valor += 3
    
    # Sumo los aciertos de los resultados y si es pleno o no
    i = j = 0
    while i < len(Usuario['Resultados']):
        if(Usuario['Resultados'][i] == Datos['Resultados'][i]):
            Valor += 2
            j += 1
            if(i == 2 and j == 3):  # Si esto se cumple, significa que ha acertado el podio completo
                Valor += 3
        i += 1
    
    # Sumo los aciertos de 1 punto
    i = 0
    while i < len(Usuario['1Puntos']):
        if(Usuario['1Puntos'][i] == Datos['1Puntos'][i]):
            Valor += 1
        i += 1

    return Valor

# Transformamos los tiempos del usuario de texto a TimeDelta
def TransformacionTiempo(Dato):

    # Si no existe tiempo (Por algún motivo), entonces le ponemos un tiempo largo
    if(Dato == 'None' or Dato == 'NONE'):
        delta = timedelta(days=0, hours=0, minutes=60, seconds=0, microseconds=0)
    else:
        Dato = Dato.replace('.', ':')
        Tiempo = datetime.strptime(Dato, '%M:%S:%f')
        delta = timedelta(days=0, hours=0, minutes=Tiempo.minute, seconds=Tiempo.second, microseconds=Tiempo.microsecond)

    return delta

# Translado la información a las antiguas porras y limpio
def LimpiarBaseDatos(BaseDatos, DatosGP):
    PorrasAnteriores.append_row([DatosGP['NombreGP'], str(BaseDatos['PABLO']), str(BaseDatos['JOSEMA']), str(BaseDatos['RAUL']), str(BaseDatos['MIGUEL']), '.', str(DatosGP), '.'])

    # Voy a poner todos los datos de la base de datos a 'None'
    for i in BaseDatos:
        for j in BaseDatos[i]:
            BaseDatos[i][j] = 'None'

    # Voy a actualizar la base de datos de Google teniendo los valores a 'None'
    cell_list = Datos.range('B2:E8')
    for cell in cell_list:
        cell.value = 'None'
    Datos.update_cells(cell_list)
    Datos.update('H100:K100', [['None', 'None', 'None', 'None']])

# Muestra el nombre de las carreras realizadas
def CarrerasRealizadas():
    return PorrasAnteriores.col_values(1)

# Genera mensaje de puntuaciones de un usuario
def MensajepuntosCarrera(Nombre, Carrera):
    Columna = {'PABLO': 2, 'JOSEMA': 3, 'RAUL': 4, 'MIGUEL': 5}
    PorraAntigua = PorrasAnteriores.col_values(Columna[Nombre])
    Index = int(Carrera) - 1
    Dict = PorraAntigua[Index]
    print(Dict)
    Dict = ast.literal_eval(Dict)
    print(Dict['Pole'])