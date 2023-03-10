class Device:

    instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls)

            #attributes
            cls.instance.clients = 0
            cls.instance.status = False
            cls.info_json = []

        return cls.instance

    def __init__(self) -> None:
        pass

    def get_instance(cls):
        if cls.instance is None:
            return 

    def get_clients(self):
        return self.clients

    def set_clients(self, clients):
        self.clients = clients

    def get_info_json(self):
        return self.info_json
    
    def set_info_json(self, info_json):
        self.info_json = info_json
    
    def add_info_json(self, info):
        self.info_json.append(info)


