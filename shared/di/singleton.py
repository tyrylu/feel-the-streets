class Singleton:
    def __init__(self, cls=None, factory=None, *args, **kwargs):
        if not cls and not factory:
            raise ValueError("Either class or factory is required.")
        self._cls = cls
        self._factory = factory
        self._instance = None
        self._args = args
        self._kwargs = kwargs

    def __call__(self):
        if not self._instance:
            if self._factory:
                to_call = self._factory
            else:
                to_call = self._cls
            self._instance = to_call(*self._args, **self._kwargs)
        return self._instance
    
    def set_call_args(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs