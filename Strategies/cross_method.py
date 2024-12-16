import backtrader as bt
from strategies.general_strategy import GeneralStrategy

class CrossMethod(GeneralStrategy):        
    """
    Implementación de estrategia de cruce de medias móviles. Esta utiliza una SMA con un cierto período
    para generar señales de compra y venta cuando el precio de cierre cruza la SMA.

    Atributos:
        smas (dict[bt.feeds.Data, bt.indicators.SimpleMovingAverage]): Indicadores SMA utilizados para cada datafeed.

    Args:
        period (int): El número de períodos para calcular la SMA, este posee un valor por defecto de 10.
    """

    params = (
        ('period', 10),
    )

    def __init__(self):
        """
        Para inicializar la estrategia y calcula las SMAs utilizando el período proporcionado junto con el precio de cierre
        de los datos.
        """
        super().__init__()

        self.smas = {}

        for data in self.datas:
            self.smas[data._name] = bt.indicators.SimpleMovingAverage(data.close, period=self.params.period)

    def conditions_buy(self, data) -> bool:
        """
        Método que define las condiciones para ejecutar una orden de compra (implementación del método de la clase genérica de estrategia).

        La orden de compra se genera cuando el precio de cierre está por encima del valor de la SMA.

        Args:
            data (bt.feeds.YahooFinanceCSVData): Objeto de datos de Yahoo Finance con la información del activo correspondiente.

        Returns:
            bool: Verdadero si el precio de cierre es mayor que la SMA, lo que indica una señal de compra (por posible tendencia alcista).
        """
        return data.close[0] > self.smas[data._name][0]

    def conditions_sell(self, data) -> bool:
        """
        Método que define las condiciones para ejecutar una orden de venta (implementación del método de la clase genérica de estrategia).

        La orden de venta se genera cuando el precio de cierre está por debajo del valor de la SMA.

        Args:
            data (bt.feeds.YahooFinanceCSVData): Objeto de datos de Yahoo Finance con la información del activo correspondiente.

        Returns:
            bool: Verdadero si el precio de cierre es menor que la SMA, lo que indica una señal de venta (ya que indica posible tendencia bajista).
        """
        return data.close[0] < self.smas[data._name][0]
    
    def __str__(self) -> str:
        """
        Devuelve una representación en cadena de la estrategia, mostrando el nombre de la estrategia y el período de la SMA utilizada.

        Returns:
            str: Representación en cadena de la estrategia.
        """
        return f"CrossMethod con periodo de: {self.params.period}"