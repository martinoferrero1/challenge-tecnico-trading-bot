import backtrader as bt
from strategies.general_strategy import GeneralStrategy

class GoldenDeathCross(GeneralStrategy):
    """
    Implementación de estrategia basada en el cruce de dos SMA para identificar los eventos de Golden Cross y Death Cross.
    Si la SMA de corto plazo cruza hacia abajo la de largo plazo de trata de un Death Cross (por lo que se vende ya que indica
    prosible tendencia bajista), mientras que si la SMA de corto plazo cruza hacia arriba la de largo plazo se trata de un Golden
    Cross, lo que indica una posible tendencia alcista y se compra.

    Atributos:
        smas_short_period (dict[bt.feeds.Data, bt.indicators.SimpleMovingAverage]): SMAs para el período corto (una por cada datafeed).
        smas_long_period (dict[bt.feeds.Data, bt.indicators.SimpleMovingAverage]): SMAs para el período largo (una por cada datafeed).

    Args:
        short_period (int): El número de períodos para calcular la SMA corta, siendo que su valor por defecto es de 50.
        long_period (int): El número de períodos para calcular la SMA larga, siendo que su valor por defecto es de 200.
    """

    params = (
        ('short_period', 10),
        ('long_period', 30),
    )

    def __init__(self):
        """
        Para inicializar la estrategia y calcula las SMAs cortas y largas utilizando los períodos proporcionados
        junto con el precio de cierre de los datos.
        """
        super().__init__()

        self.smas_short_period = {}
        self.smas_long_period = {}
        
        for data in self.datas:
            self.smas_short_period[data._name] = bt.indicators.SimpleMovingAverage(data.close, period=self.params.short_period)
            self.smas_long_period[data._name] = bt.indicators.SimpleMovingAverage(data.close, period=self.params.long_period)

    
    def conditions_buy(self, data) -> bool:
        """
        Método que define las condiciones para ejecutar una orden de compra (implementación del método de la clase genérica de estrategia).

        La orden de compra se genera cuando la SMA de corto plazo cruza hacia arriba la de largo plazo (Golden Cross).

        Args:
            data (bt.feeds.YahooFinanceCSVData): Objeto de datos de Yahoo Finance con la información del activo correspondiente.

        Returns:
            bool: Verdadero si la SMA de corto plazo cruza hacia arriba la de largo plazo, lo que indica una señal de compra (por posible tendencia alcista).
        """

        return self.smas_short_period[data._name][0] > self.smas_long_period[data._name][0] # No está la segunda condición porque en el contexto del problema
                                                                                            # no se puede estar comprado y seguir comprando ya que antes se
                                                                                            # verifica que no haya posición, por lo que está implícito
                                                                                            # que en el candlestick previo la SMA corta no era mayor que la SMA larga.
    
    def conditions_sell(self, data) -> bool:
        """
        Método que define las condiciones para ejecutar una orden de venta (implementación del método de la clase genérica de estrategia).

        La orden de venta se genera cuando la SMA de corto plazo cruza hacia abajo la de largo plazo (Death Cross).

        Args:
            data (bt.feeds.YahooFinanceCSVData): Objeto de datos de Yahoo Finance con la información del activo correspondiente.

        Returns:
            bool: Verdadero si la SMA de corto plazo cruza hacia abajo la de largo plazo, lo que indica una señal de venta (por posible tendencia bajista).
        """
        return self.smas_short_period[data._name][0] < self.smas_long_period[data._name][0] # No está la segunda condición porque en el contexto del problema
                                                                                            # no se puede estar vendido y seguir vendiendo ya que antes se
                                                                                            # verifica que haya una posición (que además no puede ser menor a 0),
                                                                                            # por lo que está implícito que en el candlestick previo la SMA corta no era menor que la SMA larga. 
    
    def __str__(self) -> str:
        """
        Devuelve una representación en cadena de la estrategia, mostrando los períodos de las SMA corta y larga utilizadas.

        Returns:
            str: Representación en cadena de la estrategia con los períodos de las SMA.
        """
        return f"GoldenDeathCross con periodo corto de {self.params.short_period} y periodo largo de {self.params.long_period}"
    
    
    
    

    
