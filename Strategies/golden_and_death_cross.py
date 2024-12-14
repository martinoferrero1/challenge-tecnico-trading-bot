import backtrader as bt
from strategies.general_strategy import GeneralStrategy

class GoldenDeathCross(GeneralStrategy):
    """
    Implementación de estrategia basada en el cruce de dos SMA para identificar los eventos de Golden Cross y Death Cross.
    Si la SMA de corto plazo cruza hacia abajo la de largo plazo de trata de un Death Cross (por lo que se vende ya que indica
    prosible tendencia bajista), mientras que si la SMA de corto plazo cruza hacia arriba la de largo plazo se trata de un Golden
    Cross, lo que indica una posible tendencia alcista y se compra.

    Atributos:
        params (tuple): Parámetros de la estrategia. Incluye el período de las SMA cortas y largas.
        sma_short_period (bt.indicators.SimpleMovingAverage): SMA para el período corto.
        sma_long_period (bt.indicators.SimpleMovingAverage): SMA para el período largo.

    Args:
        short_period (int): El número de períodos para calcular la SMA corta, siendo que su valor por defecto es de 50.
        long_period (int): El número de períodos para calcular la SMA larga, siendo que su valor por defecto es de 200.
    """

    params = (
        ('short_period', 50),
        ('long_period', 200),
    )

    def __init__(self):
        """
        Para inicializar la estrategia y calcula las SMA corta y larga utilizando los períodos proporcionados
        junto con el precio de cierre de los datos.
        """
        super().__init__()
        self.sma_short_period = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.sma_long_period = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)

    
    def conditions_buy(self):
        """
        Método que define las condiciones para ejecutar una orden de compra (implementación del método de la clase genérica de estrategia).

        La orden de compra se genera cuando la SMA de corto plazo cruza hacia arriba la de largo plazo (Golden Cross).

        Returns:
            bool: Verdadero si la SMA de corto plazo cruza hacia arriba la de largo plazo, lo que indica una señal de compra (por posible tendencia alcista).
        """

        return self.sma_short_period[0] > self.sma_long_period[0] and self.sma_short_period[-1] < self.sma_long_period[-1] # Están ambas condiciones porque en realidad no solo debe ser mayor la SMA corta en el momento actual, sino que también debe haber sido menor en el candlestick previo, lo que indica que hubo un cruce hacia arriba.
    
    def conditions_sell(self):
        """
        Método que define las condiciones para ejecutar una orden de venta (implementación del método de la clase genérica de estrategia).

        La orden de venta se genera cuando la SMA de corto plazo cruza hacia abajo la de largo plazo (Death Cross).

        Returns:
            bool: Verdadero si la SMA de corto plazo cruza hacia abajo la de largo plazo, lo que indica una señal de venta (por posible tendencia bajista).
        """
        return self.sma_short_period[0] < self.sma_long_period[0] and self.sma_short_period[-1] > self.sma_long_period[-1] # Están ambas condiciones porque en realidad no solo debe ser menor la SMA corta en el momento actual, sino que también debe haber sido mayor en el candlestick previo, lo que indica que hubo un cruce hacia abajo.
    
    def __str__(self):
        """
        Devuelve una representación en cadena de la estrategia, mostrando los períodos de las SMA corta y larga utilizadas.

        Returns:
            str: Representación en cadena de la estrategia con los períodos de las SMA.
        """
        return f"GoldenDeathCross con periodo corto de {self.params.short_period} y periodo largo de {self.params.long_period}"
    
    
    
    

    
