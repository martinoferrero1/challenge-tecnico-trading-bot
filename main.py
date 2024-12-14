import os
from datetime import datetime
import backtrader as bt

from strategies.cross_method import CrossMethod
from strategies.golden_and_death_cross import GoldenDeathCross

DATA_FOLDER = 'data'
CASH = 100000.0
START_DATE = datetime(2021, 1, 1)
END_DATE = datetime(2021, 12, 31)

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

def create_cerebro(data_folder, initial_cash):
    """
    A partir de esta función se crea y configura el motor cerebro de Backtrader.

    Args:
        data_folder (str): Carpeta que contiene los archivos CSV de los datafeeds.
        initial_cash (float): Monto inicial para el portafolio.

    Returns:
        cerebro (bt.Cerebro): Motor cerebro configurado con datafeeds y estrategias.
    """
    cerebro = bt.Cerebro()

    datafeeds = load_datafeeds(data_folder)

    for datafeed, name in datafeeds:
        cerebro.adddata(datafeed, name=name)

    cerebro.addstrategy(CrossMethod)
    cerebro.addstrategy(CrossMethod, period=30)
    cerebro.addstrategy(GoldenDeathCross)

    cerebro.broker.setcash(initial_cash)

    return cerebro

if __name__ == '__main__':

    cerebro = create_cerebro(DATA_FOLDER, CASH)

    initial_value = cerebro.broker.getvalue()

    print(f'VALOR DE INICIO DEL PORTAFOLIO: {initial_value:.2f}')

    cerebro.run()

    final_value = cerebro.broker.getvalue()
    
    print(f'VALOR DE FIN DEL PORTAFOLIO: {final_value:.2f}')
