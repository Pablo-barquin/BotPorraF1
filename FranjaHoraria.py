from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

geolocation = Nominatim(user_agent='geoapiExercises')

def TiempoFranjaEspañola(Ciudad, HorarioGP):
    location = geolocation.geocode(Ciudad)  # Encuentro la longitud y latitud de la ciudad que quiero descubrir su localización

    obj = TimezoneFinder()
    LocalizacionGP = obj.timezone_at(lng=location.longitude, lat=location.latitude) # Obtengo su franja horaria basado en la longitud y latitud encontrada anteriormente

    HorarioGP = datetime.combine(HorarioGP.date(), HorarioGP.time())  # Uso el horario local del GP y lo convierto en Datetime

    timezoneGP = pytz.timezone(LocalizacionGP) # Creo un objeto timezone basado en la localización del GP
    HorarioGP = timezoneGP.localize(HorarioGP)  # Añado la timezone a la hora del GP

    timezoneESP = pytz.timezone('Europe/Madrid')
    TransformadoGP = HorarioGP.astimezone(timezoneESP)    # Transformo el horario del GP y el actual al horario español usando el timezone correspondiente
    HorarioESP = datetime.now().astimezone(timezoneESP)     
    TiempoRestante = TransformadoGP - HorarioESP          # Tiempo que falta desde la hora actual hasta el horario del GP

    return HorarioESP > TransformadoGP, custom_format(TiempoRestante), TransformadoGP


def custom_format(td):
    minutes, seconds = divmod(td.seconds, 60)   # Divido los segundos totales entre 60, para obtener los minutos y los segundos
    hours, minutes = divmod(minutes, 60)        # Divido los minutos anteriores entre 60, para obtener las horas
    formatted = '{:d}_horas,_{:02d}_minutos,_{:02d}_segundos'.format(hours, minutes, seconds)    # Devuelvo un string siguiendo ese formato. :d significa que el valor será en decimal, mientras que :02d significa que si tiene 7 minutos, pues será 07, y si tiene 14 minutos, será 14
    if td.days:     # Si existen dias, lo añadimos delante de nuestra cadena anteriormente creada
        formatted = '{}_dia{},_{}'.format(td.days, 's' if td.days > 1 else '', formatted) # Si es mas de un dia, le añadimos la 's'
    return formatted