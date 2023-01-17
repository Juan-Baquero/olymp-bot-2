from subprocess import check_output
from datetime import timezone
import pandas as pd
from shared.indicadores import lazyModel
from shared.data import metatrader
from shared.data import datos
from shared.data import mongo_db
from shared import estrategias
from bot import web_scraping

from os import system
from datetime import datetime as dt
import pytz
from datetime import datetime
import ntplib
from time import ctime
c = ntplib.NTPClient()


# establecemos el huso horario en UTC
timezone = pytz.timezone("Etc/UTC")


""" def obtenerAccion(indicador, model, datos):
    if indicador == "ema":
        return ema.getActions(datos)
    if indicador == 'stoch-qstick':
        return stochastic.getActions(datos) """


def obtenerMinuto(minuto):
    try:
        response = c.request(
            'pool.ntp.org', version=3)
        array = ctime(response.tx_time).split(':')
        print(array[2])
        return int(array[1])
    except:
        print('error obtener fecha')
        return minuto


def ejecutar():
    global symbol, indicator, isMt5Started
    symbol = "EURUSD"
    indicator = "lazy"  # "ema"  # "stoch-qstick" "lazy"
    model = "DecisionTreeRegressor"

    web_scraping.startBot()
    while True:
        isMt5Started = False
        successful = False
        mt5 = None
        accion = None
        try:
            check_output("cd C:\Windows\System32", shell=True)
            check_output("w32tm /resync", shell=True)

            # INICIAR METATRADER
            while (not isMt5Started):
                mt5 = metatrader.init(symbol)
                if(mt5 == None):
                    isMt5Started = False
                else:
                    isMt5Started = True

            # OBTENER DATOS WEB
            rate = web_scraping.getRate()
            balance = web_scraping.getBalance()
            last_rate = mongo_db.getLastRate()
            print('Inicio')
            print('rate', rate)
            print('balance', balance)
            if(not last_rate == rate):
                mongo_db.insertRate({"rate": rate,
                                    "utc_time": datetime.now(tz=timezone),
                                     "time": datetime.now()})
            # LIMPIA LA CONSOLA CADA DIA
            if(dt.now(tz=timezone).hour == 0):
                system("cls")

            # ESPERA A QUE SEA EL SEGUNDO 30
            ahora = dt.now(tz=timezone)
            while not (ahora.second == 30):
                ahora = dt.now(tz=timezone)

            # SE CALCULA PREDICCIONES
            step = 1000  # Cantidad de datos
            posicion = 0  # Posicion actual

            # Se obtienen los ultimos datos
            datos_todos = datos.obtenerDatos(
                mt5, symbol,  cantidad=step, posicion=posicion)

            # Se obtiene obtiene predicción para el siguiente minuto
            # CLOSE
            datos_train, X_test = lazyModel.obtenerDatos(
                datos_todos.copy(), 'close')
            pred_close = lazyModel.obtenerPrediccion(
                model, datos_train, 'close', X_test)[0]
            # LOW
            datos_train, X_test = lazyModel.obtenerDatos(
                datos_todos.copy(), 'low')
            pred_low = lazyModel.obtenerPrediccion(
                model, datos_train, 'low', X_test)[0]
            # HIGH
            datos_train, X_test = lazyModel.obtenerDatos(
                datos_todos.copy(), 'high')
            pred_high = lazyModel.obtenerPrediccion(
                model, datos_train, 'high', X_test)[0]

            barra_actual = datos.obtenerDatos(mt5,
                                              symbol,  cantidad=1, posicion=0)

            # Se obtienen valores para calcular accion
            open = barra_actual['open'][len(barra_actual)-1]
            open_1 = datos_todos['open'][len(datos_todos)-1]
            close_1 = datos_todos['close'][len(datos_todos)-1]
            high_1 = datos_todos['high'][len(datos_todos)-1]
            low_1 = datos_todos['low'][len(datos_todos)-1]
            # Se obtiene la accion
            accion = estrategias.obtenerAccion(4, pred_close, pred_low, pred_high,
                                               open, open_1, close_1, low_1, high_1)

            action_time = X_test.iloc[0]['time']
            utc_time = pd.to_datetime(action_time, unit='s')
            minuto_next = int(X_test.iloc[0]['minute'])

            print('accion', minuto_next, accion)

            # SE OBTIENE LA ULTIMA ACCION
            while not (ahora.second == 58):
                ahora = dt.now(tz=timezone)

            global last_action_time
            try:
                last_operacion = mongo_db.getLast(indicator)[0]
                last_action_time = last_operacion['action_time']
            except:
                last_action_time = 0
            # Versiones no Lazy
            # rates = metatrader.getRatesPos(mt5)
            # acciones = obtenerAccion(indicator, model, rates)

            # Se espera a que coincida el siguiente minuto
            minuto = dt.now(tz=timezone).minute
            #minuto = obtenerMinuto(m)
            while not minuto == minuto_next:
                minuto = dt.now(tz=timezone).minute
                #minuto = obtenerMinuto(minuto)
            # SE EJECUTA LA ACCION
            if(accion == 'buy' and rate > 0):
                web_scraping.clickUp()
            elif(accion == 'sell' and rate > 0):
                web_scraping.clickDown()
            else:
                accion = None

            amount = web_scraping.getAmount()
            duration = web_scraping.getDuration()
            utc_time_current = datetime.now(tz=timezone)
            successful = True
            print('Fin minuto')
            # FINALIZAR METATRADER
            if(isMt5Started):
                metatrader.end(mt5)

        except Exception as e:
            if(isMt5Started):
                metatrader.end(mt5)
            successful = False
            isMt5Started = False
            print(
                f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
            break
            # web_scraping.startBot()

        if(not(accion == None) and successful):

            mongo_db.insertOperation(
                {"indicator": indicator+'_'+model,
                 "operation": accion,
                 'open': int(barra_actual['open']),
                 'pred_close': pred_close,
                 "action_time": int(action_time),
                 "utc_time": utc_time,
                 "utc_time_current": utc_time_current,
                 "currency": "EURUSD",
                 "rate": rate,
                 "amount": amount,
                 "duration": duration,
                 "balance": balance})
        # sleep(2)


ejecutar()
