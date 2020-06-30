import os
import logging
import time

from rx import operators as op

from mamba.core.msg import Log, LogLevel
from mamba.core.component_base import Component


class Logger(Component):
    def __init__(self, context, local_config=None):
        super(Logger, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Initialize observers
        self._register_observers()

        # create logger with 'mamba_application'
        self._logger = logging.getLogger('mamba_logger')
        self._logger.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '[%(levelname)s] [%(asctime)s] %(message)s', "%Y%m%dT%H%M%S")

        # create console handler with a higher
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)

        ch.setFormatter(formatter)
        # add the handlers to the logger

        self._logger.addHandler(ch)

        if context.get('project_dir') is not None:
            # create file handler for logs
            timestamp = time.strftime("%Y%m%dT%H%M%S")
            fh = logging.FileHandler(
                os.path.join(context.get('project_dir'), 'log',
                             f'{timestamp}.log'))
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            self._logger.addHandler(fh)

    def _register_observers(self):
        # Register to the raw_tc provided by the socket server service
        self._context.rx['log'].pipe(
            op.filter(lambda value: isinstance(value, Log))).subscribe(
                on_next=self._received_log)

    def _received_log(self, log: Log):
        """ Entry point for processing a new msg telecommand coming from the
            socket server.

            Args:
                raw_tc (Log): The msg telecommand coming from
                                         the socket.
        """
        msg = f'[{log.src}] {log.msg}'

        if log.level == LogLevel.Dev:
            self._logger.debug(msg)
        elif log.level == LogLevel.Info:
            self._logger.info(msg)
        elif log.level == LogLevel.Warning:
            self._logger.warning(msg)
        else:
            self._logger.error(msg)


#
#
#
# self.logger.debug(f'Register service: {command.encode("utf-8")}')
