import logging
import serial

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.serial import SerialDataEvent

class SerialBackend(Backend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = None

    def send_message(self, msg):
        pass

    def get_data(self):
        plugin = get_plugin('serial')
        return plugin.get_data().output

    def run(self):
        super().run()
        logging.info('Initialized serial backend')

        while not self.should_stop():
            new_data = self.get_data()
            if self.data is None or self.data != new_data:
                self.bus.post(SerialDataEvent(data=new_data))

            self.data = new_data


# vim:sw=4:ts=4:et:

