class Device:

    instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls)

            #attributes
            cls.instance.device_clients = 0

        return cls.instance

    def __init__(self) -> None:
        pass

    def get_instance(cls):
        if cls.instance is None:
            return 

    def get_device_clients(self):
        return self.device_clients

    def set_device_clients(self, device_clients):
        self.device_clients = device_clients