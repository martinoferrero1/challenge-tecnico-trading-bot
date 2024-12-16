import os
from datetime import datetime
import backtrader as bt

from strategies.general_strategy import GeneralStrategy
from strategies.cross_method import CrossMethod
from strategies.golden_and_death_cross import GoldenDeathCross

DATA_FOLDER = 'data'
LOGS_FOLDER = 'logs'
LOGS_FILE = 'operations.log'
CASH = 100000.0
START_DATE = datetime(2021, 1, 1)
END_DATE = datetime(2022, 1, 1)

def load_datafeeds(data_folder):
    """
    Esta función carga todos los archivos CSV de la carpeta especificada para los datafeeds.

    Args:
        data_folder (str): Ruta a la carpeta que contiene los archivos CSV de los datafeeds.

    Returns:
        list: Lista de objetos YahooFinanceCSVData (se usa este ya que están previamente descargados, sino se usaría YahooFinanceData).
    """
    datafeeds = []
    files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

    for file in files:
        datafeed = bt.feeds.YahooFinanceCSVData(
            dataname=os.path.join(data_folder, file),
            fromdate=START_DATE,
            todate=END_DATE
        )
        datafeeds.append((datafeed, file.split('.')[0]))
    
    return datafeeds

def create_logs_file():
    """
    Crea la carpeta de logs y el archivo operations.log si no existen.
    Vacía el archivo si ya existe.

    Returns:
        str: Ruta al archivo de logs.
    """
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)
    log_file_path = os.path.join(LOGS_FOLDER, LOGS_FILE)
    with open(log_file_path, 'w') as log_file:
        log_file.truncate(0)
    
    return log_file_path

def create_cerebro(log_file_path):
    """
    A partir de esta función se crea y configura el motor cerebro de Backtrader.

    Args:
        log_file_path (str): Ruta al archivo de logs.

    Returns:
        cerebro (bt.Cerebro): Motor cerebro configurado con datafeeds y estrategias.
    """
    cerebro = bt.Cerebro()

    datafeeds = load_datafeeds(DATA_FOLDER)

    for datafeed, name in datafeeds:
        cerebro.adddata(datafeed, name=name)

    GeneralStrategy.log_file_path = log_file_path
    #GeneralStrategy.show_generated_order_log = True #Descomentar si se quiere ver también los logs de las órdenes generadas pero en proceso

    cerebro.addstrategy(CrossMethod)
    cerebro.addstrategy(CrossMethod, period=30)
    cerebro.addstrategy(GoldenDeathCross)

    cerebro.broker.setcash(CASH)

    return cerebro

if __name__ == '__main__':

    log_file_path = create_logs_file()

    cerebro = create_cerebro(log_file_path)

    initial_value = cerebro.broker.getvalue()

    with open(log_file_path, 'a') as log_file:
        log_file.write(f'VALOR DE INICIO DEL PORTAFOLIO: {initial_value:.2f}\n')

    cerebro.run()

    final_value = cerebro.broker.getvalue()
    
    with open(log_file_path, 'a') as log_file:
        log_file.write(f'VALOR DE FIN DEL PORTAFOLIO: {final_value:.2f}\n')
