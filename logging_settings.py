import logging
import os.path

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='logs/script-logs.log',
                    filemode='a')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

# Now, we can log to the root logger, or any other logger. First the root...

# Now, define a couple of other loggers which might represent areas in your
# application:

log_start = logging.getLogger('INITIATING SCRIPT - ')
log_trade = logging.getLogger('TRADE STARTED - ')
log_buy = logging.getLogger('TRADE | BUY - ')
log_sell = logging.getLogger('TRADE | SELL - ')
log_data_pull = logging.getLogger('DATA PULL - ')
log_error = logging.getLogger('ERROR - ')
log_trade_indicator = logging.getLogger('TBD')
logger8 = logging.getLogger('TBD')
