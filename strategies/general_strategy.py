import backtrader as bt

class GeneralStrategy(bt.Strategy):
    """
    Clase base para estrategias concretas.
    Permite gestionar compras y ventas automáticas basadas en condiciones definidas.

    Atributos de clase:
        log_file_path (str): Ruta al archivo de log. Por defecto es 'logs/operations.log'.
        show_generated_order_log (bool): Indica si mostrar o no el log de órdenes generadas en el next, pero que están en proceso (ni ejecutadas, ni canceladas, etc). Por defecto no se muestra.
        pending_operation_funds (int): Monto de dinero pendiente de operaciones, para evitar que una operación de compra utilice fondos de otra operación de compra que todavía no se ha completado.


    Atributos:
        log_file (file): Archivo de log para registrar las operaciones realizadas, se guarda en la carpeta logs del proyecto.
        assets_registry (dict): Registro de activos y sus respectivas cantidades para la estrategia, para saber cuántos activos se tienen en cartera disponibles para vender con la estrategia.
    Args:
        investment_fraction (float): Fracción del portafolio a invertir en cada activo. Por defecto es 0.1, o sea el 10% del portafolio.
    """

    log_file_path = 'logs/operations.log'

    show_generated_order_log = False

    pending_operation_funds = 0
    
    params = (
        ('investment_fraction', 0.1),
        ('log_file_path', 'logs/operations.log'),
    )

    def __init__(self):
        """
        Inicializa la estrategia y el registro de activos con 0 unidades de cada uno. Además, abre el archivo de log para registrar
        las operaciones.
        """
        self.assets_registry = {}
        for data in self.datas:
            self.assets_registry[data._name] = 0    # Si bien podria ser un atributo de clase, cada instancia de estrategia solo deberia conocer sus
                                                    # propias cantidades de activos. No hay problema con esto porque no tendria sentido pasar al cerebro dos estrategias del mismo tipo con iguales indicadores, por lo que cada una es diferente y no se mezclan.

        self.log_file = open(self.params.log_file_path, 'a', buffering=1)   # A partir de setear el buffering en 1 se asegura que el archivo se
                                                                            # escriba en cada operación en orden, lo cual es crucial ya que sino pueden ocurrir problemas en el orden
                                                                            # de los registros (y es más eficiente al no hacer un flush en cada escritura)
        
    def add_log_entry(self, txt, dt=None):
        """
        Registra un mensaje con la fecha correspondiente.

        Args:
            txt (str): Mensaje a registrar.
            dt (datetime): Fecha asociada al mensaje.
        """
        if dt is None:
            dt = self.datas[0].datetime.date(0) # Para que si no se pasa una fecha, se utilice la del candlestick actual del primer datafeed
        if self.log_file:
            self.log_file.write(f"{dt.isoformat()}, {txt}" + '\n')
        
    def get_purchase_vol(self, data) -> int:
        """
        Este método calcula el tamaño de la posición a comprar basado en la fracción del portafolio que se puede utilizar.

        Args:
            data (bt.feeds.YahooFinanceCSVData): Objeto de datos de Yahoo Finance con la información del activo correspondiente.

        Returns:
            int: Tamaño de la posición a comprar.
        """
        total_value = self.broker.getvalue()
        money_to_invest = total_value * self.params.investment_fraction
        available_funds = self.broker.get_cash() - GeneralStrategy.pending_operation_funds

        if money_to_invest <= available_funds:
            size = int(money_to_invest / data.close[0])
            return size
        
        return 0 # Si bien podría quitarse el if y retornar directamente el resultado de la división porque el money_to_invest en este contexto no debiera ser nunca negativo, no está de más el chequeo
    
    def conditions_buy(self, data) -> bool:
        """
        Método que define las condiciones para ejecutar una orden de compra (debe ser implementado por las clases hijas).

        Args:
            data (bt.feeds.YahooFinanceCSVData): Objeto de datos de Yahoo Finance con la información del activo correspondiente.

        Returns:
            bool: Verdadero si se cumplen las condiciones de compra.
        """
        return True
    
    def conditions_sell(self, data) -> bool:
        """
        Método que define las condiciones para ejecutar una orden de venta (debe ser implementado por las clases hijas).

        Args:
            data (bt.feeds.YahooFinanceCSVData): Objeto de datos de Yahoo Finance con la información del activo correspondiente.

        Returns:
            bool: Verdadero si se cumplen las condiciones de venta.
        """
        return True
        
    def next(self):
        """
        Este método es la lógica principal de la estrategia, ejecutado en cada paso de cada datafeed. En caso de que no se cuente
        con una posición (cuando es de 0 en el assets_registry para ese activo) y se cumpla con las condiciones específicas de la
        estrategia, se genera la orden siempre y cuando sea por un volumen mayor a 0. Para las ventas debe cumplirse tanto las
        condiciones propias de la estrategia como que se tenga una posición, y se vende tanto como la misma indique a través del
        assets_registry para ese activo. Se actualiza si corresponde el monto de fondos pendientes de operaciones de compra.
        
        IMPORTANTE: De esta forma solo se pueden vender activos comprados a través de la misma estrategia, porque no se puede
        vender si no hay posición, y tampoco podría ser negativa ya que se vende lo que se tiene en posición para ese activo en la estrategia.
        """
        for data in self.datas:
            position_data = self.assets_registry.get(data._name)
            if position_data == 0 and self.conditions_buy(data):
                vol = self.get_purchase_vol(data)
                if vol > 0:
                    GeneralStrategy.pending_operation_funds += vol * data.close[0] # Se reserva el dinero para la operación recién acá porque antes aún no se sabe si se va a generar la orden
                    if GeneralStrategy.show_generated_order_log:
                        self.add_log_entry('ORDEN DE COMPRA GENERADA, ACTIVO: %s, PRECIO: %.2f, CANTIDAD: %i' % 
                            (data._name, data.close[0], vol), self.datas[0].datetime.date(0))
                    self.buy(data=data._name, size=vol)

            elif position_data > 0 and self.conditions_sell(data): # La verificación de posición ya impide que se venda si es 0, o sea que va a haber que comprar primero, y nunca se venderá algo que no se tiene
                if GeneralStrategy.show_generated_order_log:
                    self.add_log_entry('ORDEN DE VENTA GENERADA, ACTIVO: %s, PRECIO: %.2f, CANTIDAD: %i' % 
                        (data._name, data.close[0], position_data), self.datas[0].datetime.date(0))
                self.sell(data=data._name, size=position_data)  # Al vender lo que indica la posición respecto al activo en sí, que es
                                                                # independiente para cada estrategia, ya se impide que quede en una posición
                                                                # negativa, cumpliendo con la restricción de que se vende a partir de la misma estrategia de compra y que solo se vende lo que se tiene,
                                                                # porque cada estrategia vende lo que tiene en su posición

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
        Este método maneja órdenes completadas, actualizando tanto el assets_registry como el fondo destinado a operaciones
        pendientes, según corresponda. También agrega logs para dichas órdenes.

        Args:
            order (Order): Objeto de orden completada.
        """
        if order.isbuy():
            GeneralStrategy.pending_operation_funds -= order.executed.size * order.data.close[0] # Al haberse completado la orden de compra se restan los fondos reservados para la misma
            self.add_log_entry('COMPRA EJECUTADA CON ESTRATEGIA DE %s, ID: %i, ACTIVO: %s, PRECIO: %.2f, COSTO: %.2f, CANTIDAD: %i, %.2f%% DE LA CARTERA UTILIZADO' % 
                (str(self), order.ref, order.data._name, order.executed.price, order.executed.value, order.executed.size, self.params.investment_fraction * 100), self.datas[0].datetime.date(0))

        elif order.issell():
            self.add_log_entry('VENTA EJECUTADA CON ESTRATEGIA DE %s, ID: %i, ACTIVO: %s, PRECIO: %.2f, COSTO: %.2f, CANTIDAD: %i' % 
                (str(self), order.ref, order.data._name, order.executed.price, order.executed.value, order.executed.size), self.datas[0].datetime.date(0))
        else: return # Si bien en este contexto no debería darse, hay otras posibilidades además de isbuy() y issell(), donde no debería ejecutarse la última línea

        self.assets_registry[order.data._name] += order.executed.size   # Tanto si era una orden de compra como si era de venta, se
                                                                        # hace la suma (porque si era una orden de compra se compró
                                                                        # algo y la posición debe aumentar, y si era de venta se
                                                                        # vendió algo, pero el size era negativo por lo que termina siendo una resta de la cantidad de activos vendidos)


    def handle_not_completed_order(self, order):
        """
        Para manejar órdenes no completadas debido a cancelaciones, rechazos o margen insuficiente. Actualiza el fondo destinado
        si se trataba de una orden de compra. Además, agrega logs para dichas órdenes.

        Args:
            order (Order): Objeto de orden no completada.
        """
        if order.isbuy():
            amount_released = order.size * order.data.close[0]
            GeneralStrategy.pending_operation_funds -= amount_released # Lo calculo antes para mostrar el dinero que libera la operación en el log
            self.add_log_entry('ORDEN CANCELADA/MARGEN INSUFICIENTE/RECHAZADA, ID: %i, ACTIVO: %s, DINERO RESERVADO LIBERADO: %.2f' % 
                (order.ref, order.data._name, amount_released), self.datas[0].datetime.date(0))
        elif order.issell():
            self.add_log_entry('ORDEN CANCELADA/MARGEN INSUFICIENTE/RECHAZADA, ID: %i, ACTIVO: %s' % 
                (order.ref, order.data._name), self.datas[0].datetime.date(0))

    def notify_trade(self, trade):
        """
        Este método notifica el estado de una operación cerrada y muestra el activo asociado, las utilidades generadas, así como el
        valor de salida del portafolio tras la operación.

        Args:
            trade (Trade): Objeto de operación cerrada.
        """
        if not trade.isclosed:
            return

        portfolio_value = self.broker.get_value()
        self.add_log_entry('OPERACION CERRADA, ACTIVO: %s, UTILIDAD: %.2f, VALOR DE SALIDA DEL PORTAFOLIO: %.2f' % 
                (trade.data._name, trade.pnl, portfolio_value), self.datas[0].datetime.date(0))