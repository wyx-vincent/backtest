class Strategy:
    def execute(self, *args, **kwargs):
        raise NotImplementedError("Strategy.execute() should be overridden by specific strategy.")
