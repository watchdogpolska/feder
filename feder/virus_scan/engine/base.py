class BaseEngine:
    def send_scan(self, this_file, filename):
        raise NotImplementedError(
            "Provide 'send' in {name}".format(name=self.__class__.__name__)
        )

    def receive_scan(self, engine_id):
        raise NotImplementedError(
            "Provide 'receive_scan' in {name}".format(name=self.__class__.__name__)
        )
