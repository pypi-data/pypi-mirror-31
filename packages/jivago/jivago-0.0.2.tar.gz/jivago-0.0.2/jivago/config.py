from jivago.inject.service_locator import ServiceLocator


class AbstractBinder(object):

    def bind(self, service_locator: ServiceLocator):
        raise NotImplementedError


class AbstractContext(object):
    INSTANCE = None

    def __init__(self):
        self.serviceLocator = ServiceLocator()
        self.configure_service_locator()
        self.INSTANCE = self

    def configure_service_locator(self):
        raise NotImplementedError

    def service_locator(self) -> ServiceLocator:
        return self.serviceLocator

