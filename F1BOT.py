import logging, random

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Update)
import telegram
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext)

from F1API import ObtenerHorariosGP, ObtenerInformacionGP
from GoogleSheet import (GP, CarrerasRealizadas, GuardadoDatos, CargaDatos, ActualizacionPuntos, MensajepuntosCarrera, ObtenerTokenBot) # Para guardar los datos de la porra en el google sheet

CONFIRMACION = 0
EXTRACCIONPUNTOS = 0

# Base de datos que voy a utilizar
BaseDatos = {'PABLO': {}, 'JOSEMA': {}, 'RAUL': {}, 'MIGUEL': {}}

# Para errores internos del bot
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Inicializa el bot al escribir el comando /start
def Start(update: Update, context: CallbackContext):
    NombreUsuario = update.effective_user['first_name']
    update.message.reply_text(f'{NombreUsuario}, Bienvenido a la porra F1 2022. Para saber los comandos disponibles, escriba /help')

# Canción del nano para escuchar musica
def Elnano(update: Update, context: CallbackContext):
    update.message.reply_text(f'Hay que animarse. Escuchemos la biblia')
    update.message.reply_video('https://rr1---sn-h5q7knez.googlevideo.com/videoplayback?expire=1647468963&ei=Qw0yYtCPC4SNyAXPyLHwCQ&ip=185.245.84.30&id=o-AJP6fXcj86z-h1Lu4V_GscoFxCRB3Rbnp3xOvr2ZNjwj&itag=18&source=youtube&requiressl=yes&vprv=1&mime=video%2Fmp4&ns=UxAzhIdN2tzA4RikK68_HZ4G&gir=yes&clen=12305273&ratebypass=yes&dur=168.228&lmt=1501322794643594&fexp=24001373,24007246,24162928&c=WEB&n=hcCbnfpnNoqI9A&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cratebypass%2Cdur%2Clmt&sig=AOq0QJ8wRAIgd_Gg7Y1DIWvkAImUhBIYOy4kXWaHj_GZuczTtHPmd4gCIDyuP2DYBD9GNrVTebPSmhgGtB-yMEGeE4EQZAoajl6V&redirect_counter=1&rm=sn-5gol77l&req_id=bae046254222a3ee&cms_redirect=yes&ipbypass=yes&mh=Nl&mip=80.30.88.149&mm=31&mn=sn-h5q7knez&ms=au&mt=1647446966&mv=m&mvi=1&pl=18&lsparams=ipbypass,mh,mip,mm,mn,ms,mv,mvi,pl&lsig=AG3C_xAwRQIgGXqxIVzlAgBLC-wnGoeKyfzheM5S22qxcxxadJHPUEwCIQDlPudc47rl-9OdpsXX41ZFUWO7Rwzg2WUJ6Fv3h-0itQ%3D%3D')

# Enseña los comandos actuales del bot
def Help(update: Update, context: CallbackContext):
    update.message.reply_text('''Los comandos disponibles son los siguientes:
    /start -- Mensaje de Bienvenida
    /elnano -- Para animar los dias grises
    /porra -- Crea tu predicción del GP
    /verporra -- Mira la porra de un usuario
    /puntuaciones -- Muestra las puntuaciones actuales de la porra
    /siguienteGP -- Muestra información útil sobre el próximo GP
    ''')

# Realiza la porra usando /porra
def porra(update: Update, context: CallbackContext):  
    lista = [x.upper() for x in context.args]

    DentroDeTiempo, TiempoRestante, a = ObtenerHorariosGP(GP)
    if(DentroDeTiempo):
        update.message.reply_text(f'Error. La clasificacion del GP ya ha comenzado, por lo tanto usted no puede editar ni realizar una nueva porra para este GP. ATENTO AL PRÓXIMO DIA')
    elif(len(lista) != 36):   # Comprobamos que se reciben todos los datos
        update.message.reply_text(f'Error. El formato introducido de porra no es el esperado o faltan datos por rellenar. RECUERDA AÑADIR TU NOMBRE AL LADO DE /porra. Vuelva a intentarlo')
    else:
        User = CambioPorCodigo(lista) # Comprobamos si el usuario es código o nombre
        if(User not in BaseDatos.keys()): # Comprobamos que el nombre es uno de los 4 usuarios importantes
            update.message.reply_text(f'Error. El nombre o codigo del que esta haciendo la porra es incorrecto. Debe ser uno de los siguientes: Pablo, Josema, Raul, Miguel o su código despues de haber creado la porra')
        elif(BaseDatos[User]['Codigo'] != 'None' and BaseDatos[User]['Codigo'] != lista[0]):    # Si escribe el codigo, comprobamos que es el mismo. Si no tiene código, le permitimos hacer la porra
            update.message.reply_text(f'Error. Este usuario ya tiene una porra realizada. Para cambiarla, utilice el código que se te paso en el momento de realizarla')
        else:
            PorraRecibida = {}                                              # Creamos un diccionario para guardar todos los valores
            PorraRecibida.setdefault('Pole', (lista[2]))                    # Pole
            PorraRecibida.setdefault('Tiempo Pole', lista[5])               # Tiempo Pole
            PorraRecibida.setdefault('Resultados', [lista[9], lista[11], lista[13], lista[15], lista[17]])  # Resultados
            PorraRecibida.setdefault('VR (Piloto)', lista[21])              # Vuelta Rapida (Piloto)
            PorraRecibida.setdefault('P-Sainz', lista[24])                  # Puesto Sainz
            PorraRecibida.setdefault('P-Alonso', lista[27])                 # Puesto Alonso
            PorraRecibida.setdefault('1Puntos', [lista[30], lista[32], lista[35]])  # SC - Lluvia - Bandera Roja           
            
            BaseDatos[User] = PorraRecibida                             # Guardo la porra recibida en el usuario correspondiente
            update.message.reply_text(f'Los datos recogidos en resumen son los siguientes:')    # Hago un resumen al usuario de lo que ha enviado y se lo envio
            string = "Usuario: " + User + '\n'
            for key in BaseDatos[User]:
                string = string + f'{key}: {BaseDatos[User][key]}\n'
            update.message.reply_text(string)

            keyboard = [    # Creo unos botones en linea del bot, con los botones SI o NO dependiendo de lo que desee hacer
                [
                    InlineKeyboardButton("SI", callback_data='CONFIRMACION ' + User + ' ' + str(TiempoRestante)),
                    InlineKeyboardButton("NO", callback_data='CANCELAR ' + User + ' ' + str(TiempoRestante)),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.message.reply_text("¿Confirmas esta porra? Seleccione:", reply_markup=reply_markup)  # Mando por pantalla al usuario el mensaje con los botones 
            
            return CONFIRMACION

# Comprobamos que desea hacer el usuario con la porra   
def confirmacion(update: Update, context: CallbackContext):
    # El callback_query sirve para recibir lo que hace con los botones creados anteriormente.
    query = update.callback_query

    # Divido el mensaje de CONFIRMACION o CANCELAR, del nombre del usuario
    Nombre = query.data.split(' ')
    Tiempo = Nombre[2].replace('_', ' ')

    query.answer(f'Boton de {Nombre[0]} recibido')
    
    # Depende del boton que haya pulsado, recibiremos confirmacion de guardado o no
    if Nombre[0] == 'CONFIRMACION':
        query.edit_message_text(f'Has pulsado en SI')
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='GUARDAMOS LA PORRA. MUCHA SUERTE')

        BaseDatos[Nombre[1]]['Codigo'] = str(random.randint(1000,9999))
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text=f'SU CÓDIGO ES EL SIGUIENTE: {BaseDatos[Nombre[1]]["Codigo"]}\nSi desea editar su porra escriba /porra {BaseDatos[Nombre[1]]["Codigo"]}.\nSi desea ver la porra que tiene actualmente escriba /verporra {BaseDatos[Nombre[1]]["Codigo"]}')

        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text=f'\nTiempo para cerrar las porras: {Tiempo}')        

        GuardadoDatos(BaseDatos)
        return ConversationHandler.END  # Sirve para cortar la conversacion y que pueda volver a usar los comandos correctamente
    else:
        query.edit_message_text(f'Has pulsado en NO')
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='NO GUARDAMOS PORRA. Vuelva a enviarla usando /porra NOMBRE')

        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text=f'\nTiempo para cerrar las porras: {Tiempo}')

        CargaDatos(BaseDatos)        
        return ConversationHandler.END

# Función hipotética en caso de que use el comando /cancel el usuario al hacer la porra
def Cancelar(update: Update, context: CallbackContext):
    update.message.reply_text('Accion Cancelada por el usuario. Vuelva a escribir el comando correspondiente si desea repetir el proceso')
    return ConversationHandler.END

# Función para ver la porra de un usuario
def verporra(update: Update, context: CallbackContext):
    
    usuario = context.args[0].upper()
    User = CambioPorCodigo([usuario])

    if(User in BaseDatos):
        if(BaseDatos[User]['Codigo'] == 'None'):
            update.message.reply_text('Vaya, este usuario tiene actualmente la porra vacia 😪')
        elif(BaseDatos[User]['Codigo'] == usuario):
            update.message.reply_text('PORRA ENCONTRADA 😎')
            string = f'Usuario: {User} 🤓\n\nPole: {BaseDatos[User]["Pole"]} 🤫\nTiempo Pole: {BaseDatos[User]["Tiempo Pole"]}\n\nResultados Carrera:\n'
            string = string + f'1️⃣ {BaseDatos[User]["Resultados"][0]}\n2️⃣ {BaseDatos[User]["Resultados"][1]}\n3️⃣ {BaseDatos[User]["Resultados"][2]}\n4️⃣ {BaseDatos[User]["Resultados"][3]}\n5️⃣ {BaseDatos[User]["Resultados"][4]}\n\n'
            string = string + f'Puesto Sainz: {BaseDatos[User]["P-Sainz"]}\nPuesto Alonso: {BaseDatos[User]["P-Alonso"]}\n\n'
            string = string + f'🚑 Safety Car: {BaseDatos[User]["1Puntos"][0]}\n🌧 Llueve: {BaseDatos[User]["1Puntos"][1]}\n🚨 Bandera Roja: {BaseDatos[User]["1Puntos"][2]}'
        
            update.message.reply_text(string)
        else:
            update.message.reply_text('Vaya, este usuario tiene una porra activa para el proximo GP, pero necesitas escribir /verporra CODIGO, siendo CODIGO el número correspondiente de la porra para verla 👿')
    else:
        update.message.reply_text("Vaya, este usuario no existe")

# Función para ver actualizar y ver la tabla de puntuaciones #
def puntuaciones(update: Update, context: CallbackContext):
    update.message.reply_text('Cargando las puntuaciones y actualizandolas 🤖')
    PuntosActuales = ActualizacionPuntos(BaseDatos)

    update.message.reply_text(f'Las puntuaciones actuales son:\n*- Pablo:* {PuntosActuales[1]}\n*- Josema:* {PuntosActuales[2]}\n*- Raul:* {PuntosActuales[3]}\n*- Miguel:* {PuntosActuales[4]}', parse_mode=telegram.ParseMode.MARKDOWN)

# Sirve para comprobar si el usuario tiene una porra realizada y si es así, que el código sea correcto
def CambioPorCodigo(Lista):
    if Lista[0] in BaseDatos.keys():
        return Lista[0]
    else:
        for i in BaseDatos:
            if BaseDatos[i]['Codigo'] == Lista[0]:
                return i
        return 'None'

# Permite saber los puntos obtenidos de un GP específico
def verpuntosGP(update: Update, context: CallbackContext):
    
    if(len(context.args) == 0):
        update.message.reply_text('Para utilizar correctamente el comando, escriba /verpuntosGP USUARIO, siendo este uno valido de nuestra base de datos. El usuario debe ser uno de los siguientes: Pablo, Josema, Raul, Miguel')

    Nombre = context.args[0].upper()

    ListaGP = CarrerasRealizadas()
    ListaGP.pop(0)
    
    keyboard = []
    for Carreras in ListaGP:
        keyboard.append([InlineKeyboardButton(Carreras, callback_data=f'{ListaGP.index(Carreras)+2} {Nombre}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if(Nombre in BaseDatos.keys()):
        update.message.reply_text(f'Pulsa en la carrera que deseas ver los puntos de {Nombre}:', reply_markup=reply_markup) 
        return EXTRACCIONPUNTOS
    else:
        update.message.reply_text('Error, este usuario no existe en nuestra base de datos. El usuario debe ser uno de los siguientes: Pablo, Josema, Raul, Miguel')
        return ConversationHandler.END

# Sabiendo el usuario y la carrera, mostramos sus puntos
def extraccionpuntos(update: Update, context: CallbackContext):
    query = update.callback_query

    Lista = query.data.split(' ')
    context.bot.send_message(chat_id=update.effective_chat.id,
                            text=str(Lista[0]))

    MensajepuntosCarrera(Lista[1], Lista[0])

    return ConversationHandler.END

# Muestra información sobre el siguiente GP, con el horario de la clasificación y de la carrera
def siguienteGP(update: Update, context: CallbackContext):
    Carrera, Tipo, Clasif, HCarrera = ObtenerInformacionGP(GP)

    update.message.reply_text(f'El proximo GP es:\n*- Carrera:* {Carrera}\n*- Tipo:* {Tipo}\n*- Horario Clasificación:* {Clasif.strftime("%d/%m/%Y %H:%M")}\n*- Horario Carrera:* {HCarrera.strftime("%d/%m/%Y %H:%M")}', parse_mode=telegram.ParseMode.MARKDOWN)


def main():
    TOKEN = ObtenerTokenBot()  # Token que sirve para actualizar nuestro bot
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    #/start --- Al inicio del bot, mensaje de Bienvenida
    Bienvenida = CommandHandler('start', Start)

    #/elnano --- Pasa video/canción de Melendi
    elnano = CommandHandler('elNano', Elnano)

    #/help --- Muestra los comandos disponibles
    Ayuda = CommandHandler('help', Help)

    #/porra --- Recibe la porra del usuario
    Porra = ConversationHandler(
        entry_points=[CommandHandler('porra', porra, pass_args=True)],
        states={
            CONFIRMACION: [CallbackQueryHandler(confirmacion)],
        },
        fallbacks=[CommandHandler('cancel', Cancelar)]
    )

    #/verporra --- Ver la porra del usuario
    VerPorra = CommandHandler('verporra', verporra)

    #/puntuaciones --- Muestra las puntuaciones y las actualiza
    Tablapuntos = CommandHandler('puntuaciones', puntuaciones)

    #/verpuntosGP --- Recibe la porra del usuario
    VerPuntosGP = ConversationHandler(
        entry_points=[CommandHandler('verpuntosGP', verpuntosGP, pass_args=True)],
        states={
            EXTRACCIONPUNTOS: [CallbackQueryHandler(extraccionpuntos)],
        },
        fallbacks=[CommandHandler('cancel', Cancelar)]
    )

    #/siguienteGP --- Muestra informacion y horarios sobre el proximo GP
    SiguienteGP = CommandHandler('siguienteGP', siguienteGP)
    
    dp.add_handler(Bienvenida)
    dp.add_handler(Porra)
    dp.add_handler(elnano)
    dp.add_handler(Ayuda)
    dp.add_handler(VerPorra)
    dp.add_handler(Tablapuntos)
    dp.add_handler(VerPuntosGP)
    dp.add_handler(SiguienteGP)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    CargaDatos(BaseDatos)
    main()
