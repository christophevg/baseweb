__version__ = "0.2.0"

import logging

from pyfiglet import Figlet

logger = logging.getLogger(__name__)

custom_fig = Figlet(font='standard')

logger.info("\n" + str(custom_fig.renderText('baseweb')).rstrip() + f"  {__version__}")
