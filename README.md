# BotPorraF1
Proyecto personal utilizando APIs para crear un Bot que permita guardar apuestas sobre F1 con un grupo reducido de amigos.

La idea principal es realizar un Bot, que permita crear, editar y guardar porras entre el grupo de amigos. Posteriormente, cuando la carrera finalice, el propio Bot actualiza las puntuaciones de la porra, mediante un sistema de puntuaciones asignado personalmente. También permite saber la siguiente carrera que toca en el calendario de F1 2022 y prohíbe realizar porras posteriormente de la hora de la clasificación del sábado.

Utilizo Telegram como lugar para lanzar el bot, y Heroku para hostear el Bot de manera gratuita, manteniéndose activo 24/7 para cualquiera de los participantes de la porra. Por otro lado, para obtener toda la información relacionada con la F1, utilizo distintas APIs (ej.: fastf1) para obtener resultados de la clasificación y carrera, tiempo de pole y vuelta rápida, y más cosas como si ha existido bandera roja en la carrera, lluvia o safety car.

Por otro lado, utilizo GoogleSheet, para controlar toda la parte relacionada con el manejo de los datos de las porras y las distintas funciones (guardado, carga, eliminación, y actualizaciones) y si existe algún problema con el Bot, poder acceder de manera sencilla a los datos y cambiarlos si fueran necesario. Por último, utilizo una serie de funciones para cambiar la franja horaria de donde se realiza la carrera, a la hora local española.

(Actualmente el código no incluye las claves privadas, por seguridad)