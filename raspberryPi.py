import adafruit_ads1x15.ads1115 as ADS
import RPi.GPIO as GPIO
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
import time
import logging
import datetime
import sqlite3

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
sensor1 = AnalogIn(ads, ADS.P0)

GPIO.setmode(GPIO.BCM)
solenoide = 17
GPIO.setup(solenoide, GPIO.OUT, initial=GPIO.LOW)

sqliteConnection = sqlite3.connect('/home/elaynemorais/Documentos/tcc-back/app/main/banco.db');

def logger():
    logging.basicConfig(filename="irrigacao.log", level=logging.DEBUG)
    
    logging.basicConfig(
        filename="irrigacao.log",
        level=logging.DEBUG,
        format="%(asctime)s :: %(levelno)s :: %(lineon)d")    
    
def calcularUmidade(quantidade_amostra, sensor):
    somatorio = 0
    start = 1
    
    for start in range(quantidade_amostra):
        leitura_sensor = sensor.value
        somatorio += leitura_sensor
        tensao = sensor.voltage

        logging.info("{} - Amostra {} | Leitura: {} | Tensão {}".format(datetime.datetime.now(), start, leitura_sensor, tensao))
        time.sleep(2)
        
    media = somatorio/quantidade_amostra
    logging.info("{} - Media {}".format(datetime.datetime.now(), media))

    print("media: {}".format(media))

def obterValorMapeado(leitura_sensor, VALOR_MINIMO, VALOR_MAXIMO, PercentMin, PercentMax):
    return (leitura_sensor - VALOR_MINIMO) * (PercentMax - PercentMin) / (VALOR_MAXIMO - VALOR_MINIMO) + PercentMin

def monitoramento():
    sensores = obterSensores();
    dateAndTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for sensor in sensores:
        pesoSoloUmido = sensor[8]
        pesoSoloSeco = sensor[7]
        concentracao = sensor[10]
        VALOR_MINIMO = sensor[2]
        VALOR_MAXIMO = sensor[3]
        tag = sensor[1]

        logging.info("{} pesoSoloUmido: {} | pesoSoloSeco: {} | concentracao: {} | VALOR_MINIMO: {} | VALOR_MAXIMO: {} | tag: {}".format(datetime.datetime.now(), pesoSoloUmido, pesoSoloSeco, concentracao, VALOR_MINIMO, VALOR_MAXIMO, tag))

        if concentracao is None:
            concentracao = (pesoSoloUmido/pesoSoloSeco) * 100

        leitura_sensor = sensor1.value    
        leitura_sensor = obterValorMapeado(leitura_sensor, VALOR_MINIMO, VALOR_MAXIMO, 100, 0)

        logging.info("{} VALOR_MAXIMO: {} | VALOR_MINIMO: {} | CONCENTRACAO_MINIMA: {} | LEITURA_SENSOR: {}".format(datetime.datetime.now(), VALOR_MAXIMO, VALOR_MINIMO, concentracao, leitura_sensor))

        if(leitura_sensor <= concentracao):
            situacao = "IRRIGANDO"

            logging.info(f"SITUACAO {dateAndTime}: {situacao}")
            GPIO.output(solenoide, GPIO.LOW)
            time.sleep(2)

            logging.info(f"STATUS {dateAndTime}: SOLENÓIDE LIBERA FLUXO DE AGUA | ESPERA DEZ SEGUNDOS PARA PRÓXIMA LEITURA")

            update(dateAndTime, "ABERTO", tag)

        else:
            situacao = "IRRIGADO"

            logging.info(f"SITUACAO {dateAndTime}: {situacao}")
            GPIO.output(solenoide, GPIO.HIGH)
            time.sleep(2)

            logging.info(f"STATUS {dateAndTime}: SOLENÓIDE CORTA FLUXO DE AGUA | ESPERA DEZ SEGUNDOS PARA PRÓXIMA LEITURA")
            update(dateAndTime, "FECHADO", tag)

    logging.info("ESPERA DEZ SEGUNDOS PARA PRÓXIMA LEITURA")
    time.sleep(10)

def obterSensores():
    try:
        curs=sqliteConnection.cursor()
        
        sqlite_select_query = """SELECT     
                                    sensorId, 
                                    tag, 
                                    valorCalibracaoMinimo, 
                                    valorCalibracaoMaximo, 
                                    solenoideId,
                                    p.nome, p.plantaId, 
                                    so.pesoSoloSeco, so.pesoSoloUmido, so.quantidadeAmostra, so.concentracaoMinima, so.soloId
                                from 
                                    sensores as s
                                INNER JOIN plantas as p ON p.plantaId = s.plantaId
                                INNER JOIN solos as so ON p.tipoSoloId = so.soloId"""
                              
        curs.execute(sqlite_select_query)
        records = curs.fetchall()

        print("Total de sensores encontrados:  ", len(records))
        print("Sensores encontrados:  ", (records))
        print("Exibindo sensores")

        for row in records:
            print("======================")
            print(f"sensorId: {row[0]}")
            print(f"tag: {row[1]}")
            print(f"valorCalibracaoMinimo: {row[2]}")
            print(f"valorCalibracaoMaximo: {row[3]}")
            print(f"solenoideId: {row[4]}")
            print(f"nomePlanta: {row[5]}")
            print(f"plantaID: {row[6]}")
            print(f"pesoSoloSeco: {row[7]}")
            print(f"pesoSoloUmido: {row[8]}")
            print(f"quantidadeAmostra: {row[9]}")
            print(f"concentracaoMinima: {row[10]}")
            print(f"soloId: {row[11]}")
            print(f"\n")

        curs.close()

        return records

    except Exception as e:
        print(e)

def update(dateAndTime, status, tag):
    logging.info(f"{dateAndTime} Atualizar sensor tag: {tag} no banco de dados com status: {status}")

    try:
        curs=sqliteConnection.cursor()

        sqlite_update_query = """Update SENSORES set status = ?, dataLeitura = ? where tag = ?"""
        columnValues = (status,datetime.datetime.now(),tag)

        curs.execute(sqlite_update_query, columnValues)

        sqliteConnection.commit()
        curs.close()

    except Exception as e:
        print(e)

def init():
    while (True):
        logger()   
        monitoramento()
        #monitoramento(145, 190, 30766, 17381)
        #calcularUmidade(1000, canal0)
 
init()