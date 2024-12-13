import backtrader as bt

class SMAStrategyBase(bt.Strategy):

    params = (
        ('investment_fraction', 0.1),
    )

    strategy_registry = {}

    def __init__(self):

        super().__init__()
        self.dataclose = self.datas[0].close
        self.asset_registry = {}
        
    def log(self, txt, dt=None):

        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        
    def vol_buy(self):

        total_value = self.broker.getvalue()
        money_to_invest = total_value * self.params.investment_fraction

        if money_to_invest <= self.broker.get_cash():
            size = int(money_to_invest / self.data.close[0])
            if size > 0:
                return size
        
        return 0
    
    def conditions_buy(self):
        
        pass
    
    def conditions_sell(self):

        pass
        
    def next(self):

        if not self.position and self.conditions_buy():
            vol = self.vol_buy()
            if vol > 0:
                self.log('ORDEN DE COMPRA GENERADA, PRECIO: %.2f, CANTIDAD: %i' % 
                        (self.dataclose[0], vol))
                self.buy(size=vol)

                self.asset_registry[self.data._name] = self.asset_registry.get(self.data._name, 0) + vol

        elif self.position and self.can_sell(self.data._name, self.position_size) and self.conditions_sell():
            self.log('ORDEN DE VENTA GENERADA, PRECIO: %.2f, CANTIDAD: %i' % 
                    (self.dataclose[0], self.position_size))
            self.sell(size=self.position_size)

            self.asset_registry[self.data._name] -= self.position_size
            if self.asset_registry[self.data._name] == 0: # Acá se pregunta si la cantidad de activos es igual a 0 porque no puede ser negativo, ya que el metodo can_sell se encarga de verificar si la cantidad de activos es mayor o igual a la cantidad que se quiere vender
                del self.asset_registry[self.data._name]

    def can_sell(self, asset_name, vol_to_sell):
        
        if self.asset_registry.get(asset_name, 0) >= vol_to_sell:
            return True
        return False
    
    def notify_order(self, order):

        status_actions = {
            order.Completed: self.handle_completed_order,
            order.Canceled: self.handle_not_completed_order,
            order.Margin: self.handle_not_completed_order,
            order.Rejected: self.handle_not_completed_order,
        }
        
        action = status_actions.get(order.status)
        action(order)
        self.order = None
            
    def handle_completed_order(self, order):

        if order.isbuy():
            self.log('COMPRA EJECUTADA, ID: %i, ACTIVO: %s, PRECIO: %.2f, COSTO: %.2f, CANTIDAD: %i, %.2f%% DE LA CARTERA UTILIZADO' % 
                (order.ref, order.data._name, order.executed.price, order.executed.value, order.executed.size, self.params.investment_fraction * 100))
            
            self.positions_strategy[order.data._name] += order.executed.size
        
        elif order.issell():
            self.log('VENTA EJECUTADA, ID: %i, ACTIVO: %s, PRECIO: %.2f, COSTO: %.2f, CANTIDAD: %i' % 
                (order.ref, order.data._name, order.executed.price, order.executed.value, order.executed.size))

            self.positions_strategy[order.data._name] -= order.executed.size

    def handle_not_completed_order(self, order):
        
        if order.isbuy():
            amount_released = order.executed.size * order.data.close[0]
            self.log('ORDEN CANCELADA/MARGEN INSUFICIENTE/RECHAZADA, ID: %i, ACTIVO: %s, DINERO RESERVADO LIBERADO: %.2f' % 
                (order.ref, order.data._name, amount_released))
        else:
            self.log('ORDEN CANCELADA/MARGEN INSUFICIENTE/RECHAZADA, ID: %i, ACTIVO: %s' % 
                (order.ref, order.data._name))
            
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        portfolio_value = self.broker.get_value()
        self.log('OPERACION CERRADA, UTILIDAD: %.2f, PORTFOLIO VALUE: %.2f, FECHA: %s' % 
                (trade.pnl, portfolio_value, self.datas[0].datetime.date(0)))