##
##                 Autora: Elayne Natália de Oliveira de Morais
## Para disciplina TCC - Instituto Federal da Bahia - Análise e Desenvolvimento de Sistemas
## Monitoramente da umidade de solo, irrigação automática de plantas e calibração de sensor de umidade
##                          Orientador: Manoel Neto
##

import adafruit_ads1x15.ads1115 as ADS
import RPi.GPIO as GPIO
from adafruit_ads1x15.analog_in import AnalogIn
from prometheus_client import Gauge, start_http_server
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

gh = Gauge('dht22_humidity_percent', 'Humidity percentage measured by the DHT22 Sensor')
gt = Gauge('dht22_temperature', 'Temperature measured by the DHT22 Sensor', ['scale'])

gt.labels('celsius')
gt.labels('fahrenheit')

NOME_ARQUIVO_LOGGER = 'irrigacao4.log'
CONECTION_DEFAULT = '/home/elaynemorais/Documentos/tcc-back/app/main/banco.db'
PORT = 8000

sqliteConnection = sqlite3.connect(CONECTION_DEFAULT)

def logger():
    logging.basicConfig(filename=NOME_ARQUIVO_LOGGER, level=logging.DEBUG)
    
    logging.basicConfig(
        filename=NOME_ARQUIVO_LOGGER,
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
        time.sleep(10)
        
    media = somatorio/quantidade_amostra
    logging.info("{} - Media {}".format(datetime.datetime.now(), media))

def obterValorMapeado(leitura_sensor, VALOR_MINIMO, VALOR_MAXIMO, PercentMin, PercentMax):
    return (leitura_sensor - VALOR_MINIMO) * (PercentMax - PercentMin) / (VALOR_MAXIMO - VALOR_MINIMO) + PercentMin

def monitoramento():
    sensores = GetAllSensores()
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
        gh.set(leitura_sensor)
        gt.labels('celsius').set(leitura_sensor)

        irrigacaoAutomatica(dateAndTime,tag, concentracao, leitura_sensor)

    time.sleep(10)

# Funçao que de acordo com o valor de concentracao e leitura do sensor, irriga automaticamente
def irrigacaoAutomatica(dateAndTime,tag, concentracao, leitura_sensor):
    
    if(leitura_sensor <= concentracao):

        GPIO.output(solenoide, GPIO.LOW)
        time.sleep(1)

        logging.info(f"STATUS {dateAndTime}: SOLENÓIDE LIBERA FLUXO DE AGUA | ESPERA DEZ SEGUNDOS PARA PRÓXIMA LEITURA")
        update(dateAndTime, "ABERTO", tag, concentracao)

    else:
        
        GPIO.output(solenoide, GPIO.HIGH)
        time.sleep(1)

        logging.info(f"STATUS {dateAndTime}: SOLENÓIDE CORTA FLUXO DE AGUA | ESPERA DEZ SEGUNDOS PARA PRÓXIMA LEITURA")
        update(dateAndTime, "FECHADO", tag, concentracao)

## Função que obtém todos os sensores cadastrados no banco de dados relacionado as suas respectivas plantas e solo
def GetAllSensores():
    
    logging.info(f"Método GetAllSensores")

    try:
        curs=sqliteConnection.cursor()
        
        sqlite_select_query = """SELECT     
                                    sensorId, 
                                    tag, 
                                    valorCalibracaoMinimo, 
                                    valorCalibracaoMaximo, 
                                    solenoideId,
                                    planta.nome, planta.plantaId, 
                                    solo.pesoSoloSeco, solo.pesoSoloUmido, solo.quantidadeAmostra, solo.concentracaoMinima, solo.soloId
                                from 
                                    sensores as sensor
                                INNER JOIN plantas as planta ON planta.plantaId = sensor.plantaId
                                INNER JOIN solos as solo ON planta.tipoSoloId = solo.soloId"""
                              
        curs.execute(sqlite_select_query)
        records = curs.fetchall()

        logging.info(f"Total de sensores encontrados: {len(records)}")

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

## Função que atualiza os valores do sensor de acordo com a última leitura realizada pelo sistema
def update(dateAndTime, status, tag, concentracao):

    logging.info(f"{dateAndTime} Atualizar sensor tag: {tag} no banco de dados com status: {status}")

    try:
        curs=sqliteConnection.cursor()

        query = """Update SENSORES set status = ?, dataLeitura = ? where tag = ?"""
        columnValues = (status,datetime.datetime.now(),tag)

        curs.execute(query, columnValues)

        sqliteConnection.commit()
        curs.close()

    except Exception as e:
        print(e)

def init():
    metrics_port = PORT
    start_http_server(metrics_port)

    while (True):
        logger()   
        monitoramento()
        #calcularUmidade(1000, sensor1)
 
init()
