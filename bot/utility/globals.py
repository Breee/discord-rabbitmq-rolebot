import logging

# LOGGING
logging.getLogger('discord').setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.WARNING)

logFormatter = logging.Formatter("[%(asctime)s] [%(module)s] [%(levelname)-5.5s]  %(message)s")
LOGGER = logging.getLogger('bot')

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
LOGGER.addHandler(consoleHandler)
LOGGER.setLevel(level=logging.INFO)
