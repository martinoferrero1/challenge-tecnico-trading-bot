import backtrader as bt

class GeneralStrategy(bt.Strategy):
    """
    Clase base para estrategias concretas.
    Permite gestionar compras y ventas automáticas basadas en condiciones definidas.

    Attributes: asset_registry (dict): Registro de activos y sus respectivas cantidades para la estrategia, para saber cuántos activos se tienen en cartera disponibles para vender con la estrategia.

    Args: investment_fraction (float): Fracción del portafolio a invertir en cada activo. Por defecto es 0.1, o sea el 10% del portafolio.
    """

    params = (
        ('investment_fraction', 0.1),
    )

    def __init__(self):
        """
        Este método inicializa los atributos y registros necesarios para la estrategia.
        """    
        super().__init__()
        self.asset_registry = {} # Si bien podria ser un atributo de clase, cada instancia de estrategia solo deberia conocer sus
                                # propias cantidades de activos. No hay problema con esto porque no tendria sentido pasar al cerebro dos estrategias del mismo tipo con iguales indicadores, por lo que cada una es diferente y no se mezclan.
        
    def add_log_entry(self, txt, dt=None):
        """
        Registra un mensaje con la fecha correspondiente.

        Args:
            txt (str): Mensaje a registrar.
            dt (datetime, opcional): Fecha asociada al mensaje.
        """
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        
    def get_purchase_vol(self):
        """
        Este método calcula el tamaño de la posición a comprar basado en la fracción del portafolio.

        Returns:
            int: Tamaño de la posición a comprar.
        """
        total_value = self.broker.getvalue()
        money_to_invest = total_value * self.params.investment_fraction

        if money_to_invest <= self.broker.get_cash():
            size = int(money_to_invest / self.data.close[0])
            if size > 0:
                return size
        
        return 0
    
    def conditions_buy(self):
        """
        Método que define las condiciones para ejecutar una orden de compra (debe ser implementado por las clases hijas).

        Returns:
            bool: Verdadero si se cumplen las condiciones de compra.
        """
        return True
    
    def conditions_sell(self):
        """
        Método que define las condiciones para ejecutar una orden de venta (debe ser implementado por las clases hijas).

        Returns:
            bool: Verdadero si se cumplen las condiciones de venta.
        """
        return True
        
    def next(self):
        """
        Este método es la lógica principal de la estrategia, ejecutado en cada paso del datafeed. En caso de que se cumpla con las
        condiciones y el volumen a comprar sea mayor a 0, se genera la orden siempre y cuando sea por un volumen mayor a 0,
        sumando la cantidad correspondiente al registro de ese activo en la estrategia. Para las ventas debe cumplirse tanto las
        condiciones propias de la estrategia como que la cantidad de activos a vender sea menor o igual a la cantidad disponible
        en el registro de activos de la instancia de la misma (de esta forma solo se pueden vender activos comprados a traves de la misma estrategia).
        """
        if not self.position and self.conditions_buy():
            vol = self.get_purchase_vol()
            if vol > 0:
                self.add_log_entry('ORDEN DE COMPRA GENERADA, PRECIO: %.2f, CANTIDAD: %i' % 
                        (self.datas[0].close, vol))
                self.buy(size=vol)

                self.asset_registry[self.data._name] = self.asset_registry.get(self.data._name, 0) + vol

        elif self.position and self.can_sell(self.data._name, self.position_size) and self.conditions_sell():
            self.add_log_entry('ORDEN DE VENTA GENERADA, PRECIO: %.2f, CANTIDAD: %i' % 
                    (self.datas[0].close, self.position_size))
            self.sell(size=self.position_size)

            self.asset_registry[self.data._name] -= self.position_size
            if self.asset_registry[self.data._name] == 0: # Acá se pregunta si la cantidad de activos es igual a 0 porque no puede ser negativo, ya que el metodo can_sell se encarga de verificar si la cantidad de activos es mayor o igual a la cantidad que se quiere vender
                del self.asset_registry[self.data._name]

    def can_sell(self, asset_name, vol_to_sell):
        """
        Este método verifica si se puede vender un volumen específico de un activo, en base a la cantidad de activos que se
        adquirieron y vendieron a través de la estrategia.

        Args:
            asset_name (str): Nombre del activo.
            vol_to_sell (int): Volumen a vender.

        Returns:
            bool: Verdadero si se puede vender el volumen solicitado.
        """
        if self.asset_registry.get(asset_name, 0) >= vol_to_sell:
            return True
        return False
    
    def notify_order(self, order):
        """
        Verifica sobre el estado de las órdenes y maneja sus resultados. Finalmente la orden se establece en None
        si ha sido ejecutada, ha estado fuera de margen o ha sido cancelada. 

        Args:
            order (Order): Objeto de orden.
        """
        status_actions = {
            order.Completed: self.handle_completed_order,
            order.Canceled: self.handle_not_completed_order,
            order.Margin: self.handle_not_completed_order,
            order.Rejected: self.handle_not_completed_order,
        }
        
        action = status_actions.get(order.status)
        if action: # De este modo para los casos donde la orden tiene status Submitted o Accepted no se hace nada pero tampoco se la setea en None porque no se completó aun
            action(order)
            self.order = None
            
    def handle_completed_order(self, order):
        """
        Este método maneja órdenes completadas, actualizando registros y agregando logs para las mismas.

        Args:
            order (Order): Objeto de orden completada.
        """
        if order.isbuy():
            self.add_log_entry('COMPRA EJECUTADA, ID: %i, ACTIVO: %s, PRECIO: %.2f, COSTO: %.2f, CANTIDAD: %i, %.2f%% DE LA CARTERA UTILIZADO' % 
                (order.ref, order.data._name, order.executed.price, order.executed.value, order.executed.size, self.params.investment_fraction * 100))
            
            self.positions_strategy[order.data._name] += order.executed.size
        
        elif order.issell():
            self.add_log_entry('VENTA EJECUTADA, ID: %i, ACTIVO: %s, PRECIO: %.2f, COSTO: %.2f, CANTIDAD: %i' % 
                (order.ref, order.data._name, order.executed.price, order.executed.value, order.executed.size))

            self.positions_strategy[order.data._name] -= order.executed.size

    def handle_not_completed_order(self, order):
        """
        Para manejar órdenes no completadas debido a cancelaciones, rechazos o margen insuficiente.

        Args:
            order (Order): Objeto de orden no completada.
        """
        if order.isbuy():
            amount_released = order.executed.size * order.data.close[0]
            self.add_log_entry('ORDEN CANCELADA/MARGEN INSUFICIENTE/RECHAZADA, ID: %i, ACTIVO: %s, DINERO RESERVADO LIBERADO: %.2f' % 
                (order.ref, order.data._name, amount_released))
        else:
            self.add_log_entry('ORDEN CANCELADA/MARGEN INSUFICIENTE/RECHAZADA, ID: %i, ACTIVO: %s' % 
                (order.ref, order.data._name))
            
    def notify_trade(self, trade):
        """
        Este método notifica el estado de una operación cerrada y muestra las utilidades generadas, así como el valor de salida del portafolio tras la operación.

        Args:
            trade (Trade): Objeto de operación cerrada.
        """
        if not trade.isclosed:
            return

        portfolio_value = self.broker.get_value()
        self.add_log_entry('OPERACION CERRADA, UTILIDAD: %.2f, VALOR DE SALIDA DEL PORTAFOLIO: %.2f' % 
                (trade.pnl, portfolio_value))