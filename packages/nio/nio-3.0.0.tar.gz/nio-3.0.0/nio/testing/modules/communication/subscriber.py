from nio.testing.modules.communication.manager import PubSubManager


class Subscriber(object):

    """ A version of a Subscriber useful for unit-testing """

    def __init__(self, handler, topic=None, **kwargs):
        self.handler = handler
        self.topic = topic

    def open(self):
        """ Subscribes handler to matching publishers

        """
        PubSubManager.add_subscriber(self)

    def close(self):
        """ Closes publisher.

        This method delegates functionality to notify others the
        subscriber removal via a management signal.

        """
        PubSubManager.remove_subscriber(self)
