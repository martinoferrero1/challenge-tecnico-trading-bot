# Challenge Técnico - Trading Bot 📈

Este proyecto implementa un **bot de trading** para ejecutar estrategias de compra y venta de activos utilizando la biblioteca **Backtrader**. Permite probar diferentes estrategias de trading en activos como AAPL, GOOG, MSFT y TSLA, generando un registro de operaciones.

---

## 📁 Estructura del Proyecto

```plaintext
challenge-tecnico-trading-bot/
│
├── README.md                <- Documentación del proyecto
├── main.py                  <- Script principal para ejecutar el bot de trading
│
├── data/                    <- Datos históricos de activos
│   ├── AAPL.csv
│   ├── GOOG.csv
│   ├── MFST.csv
│   └── TSLA.csv
│
├── logs/                    <- Carpeta generada al ejecutar el bot
│   └── operations.log       <- Registro de operaciones realizadas
│
└── strategies/              <- Estrategias implementadas
    ├── cross_method.py
    ├── general_strategy.py
    └── golden_and_death_cross.py
```

## ⚙️ Requisitos

Antes de ejecutar el proyecto, asegúrate de tener **Python 3.2+** instalado y la biblioteca de **Backtrader** con soporte para gráficos. Puedes instalar esta última a partir del siguiente comando:

```bash
pip install backtrader[plotting]
```

En caso de querer usar otros datafeeds para los activos, tendrán que colocarse para ello archivos csv asociados a cada uno dentro de la carpeta `data`. Estos deben contener el rango de fechas deseado para la simulación. Por defecto este rango es (2021, 1, 1) a (2022, 1, 1) en el proyecto pero puede modificarse desde el archivo main a partir de las constantes de **START_DATE** y **END_DATE** establecidas.

## 🚀 Instrucciones para Correr el Proyecto

Para ejecutar el bot de trading, sigue los siguientes pasos:

1. Clona este repositorio en tu máquina local:

   ```bash
   git clone https://github.com/martinoferrero1/challenge-tecnico-trading-bot.git
   ```

2. Cambia al directorio del repositorio:

   ```bash
   cd challenge-tecnico-trading-bot
   ```

3. Ejecuta el archivo `main.py`:

    ```bash
    python main.py
    ```

## 🗒️ Funcionamiento del Bot

1. El script `main.py` crea el ***cerebro del bot*** y le carga los datos históricos de los archivos .csv ubicados en la carpeta `data`, instancias de las estrategias de ***Golden and Death Cross*** y ***Cross Method*** de la carpeta `strategies` y un ***capital inicial***. También setea las estrategias con un ***periodo*** determinado (hay valores por defecto para los periodos) para la creación de las SMA, aparte de un valor para la ***investment_fraction*** (también hay uno por defecto). Y además crea un directorio de `logs` con un archivo base dentro llamado `operations.log`, que incluye o no los logs de órdenes generadas, lo cual depende de un atributo de clase de la estretegia general, que ***por defecto es falso*** pero que puede modificarse allí también.
2. Las estrategias crean a partir de los periodos, las respectivas ***SMAs*** para cada activo, de acuerdo a los datafeeds establecidos.
3. Se ejecutan, a partir de las estrategias, las operaciones de compra y venta simuladas utilizando ***Backtrader***. Para ello implementan la lógica y las verificaciones propias de las restricciones del problema (como que no se puede vender lo que no se tiene o que una estrategia solo puede vender lo que compró), como también las específicas de cada estrategia (para lo cual implementan los métodos de ***conditions_buy*** y ***conditions_sell***). En los casos que corresponda, generan los ***logs*** para órdenes ejecutadas, canceladas, en márgenes o rechazadas, operaciones cerradas, y si se indicó a través del booleano mencionado previamente, los de las órdenes generadas.
4. Al finalizar, se genera un archivo de registro llamado `operations.log` en la carpeta `logs`, donde se detallan las operaciones realizadas. Además, al principio del archivo aparece el valor inicial del portafolio, y al final el valor de salida del mismo.

## 📊 Salida del Proyecto

La salida principal del bot es el archivo de la ruta `logs/operations.log`, el cual contiene información detallada de cada operación ejecutada, y de cómo va cambiando el valor del portafolio, lo cual se puede apreciar a través de los registros de operaciones cerradas.

## 📦 Estrategias implementadas

#### General Strategy (general_strategy.py) 

- Estrategia general que puede ser adaptada para diversas condiciones de mercado, y distintas estrategias concretas. Tiene las restricciones incluidas de que no se puede vender algo que no se tiene y que cada estrategia puede vender solamente lo que compró. Por lo tanto, las estrategias hijas están atadas a esto.

#### Cross Method Strategy (cross_method.py)

- Estrategia basada en el cruce hacia arriba o abajo del precio de cierre de los activos respecto a una SMA determinada (aquí se utiliza una con SMA de 10 velas diarias y otra con SMA de 30 velas diarias). Cuando el precio de cierre de un activo cruza hacia arriba la SMA se compra dado que se trata de una posible tendencia alcista, y cuando la cruza hacia abajo se vende por posible tendencia bajista.

#### Golden and Death Cross Strategy (golden_and_death_cross.py)

- Estrategia basada en el cruce hacia arriba o abajo de una SMA de periodo corto respecto a una SMA de periodo largo. En este caso se usa una sola instancia de esta estrategia, a través de una SMA de un periodo corto de 10 velas diarias y una de periodo largo de 30 velas diarias. Si la SMA de periodo corto cruza hacia arriba la de periodo largo, se compra debido a posible tendencia alcista. Mientras que si la cruza hacia abajo se vende, ya que es un indicador de posible tendencia bajista.