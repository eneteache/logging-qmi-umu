class Device:

    instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls)
        return cls.instance


    def __init__(self) -> None:
        self.device_clients = 0

    def get_device_clients(self):
        return self.device_clients

    def set_device_clients(self, device_clients):
        self.device_clients = device_clients