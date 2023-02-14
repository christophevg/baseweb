__version__ = "0.1.3"

import logging
logger = logging.getLogger(__name__)

from pyfiglet import Figlet
custom_fig = Figlet(font='standard')

logger.info("\n" + str(custom_fig.renderText('baseweb')).rstrip() + f"  {__version__}")
