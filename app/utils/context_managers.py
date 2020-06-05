
# Context managers

class FileContextManager():

    def __init__(self, filename, mode, exception_to_rise):
        self.filename = filename
        self.mode = mode
        self.exception_to_rise = exception_to_rise
        self.file = None

    def __enter__(self):
        try:
            self.file = open(self.filename, self.mode)
        except Exception as e:
            raise exception_to_rise()
        return self.file

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file.close()


class GeneratorContextManager:

    def __init__(self, generator):
        self.end = False
        self.generator = generator
        self.has_next = False

    def __iter__(self):
        return self

    def __exit__(self, *args):
        end = True
        return False

    def __next__(self):
        self.current = next(self.generator)
        return self


class JSONListGeneratorContextManager(GeneratorContextManager):

    def __init__(self, generator):
        super().__init__(generator)
        self.FOR_LOOP_CONDITION = 0
        self.FOR_LOOP_VARIABLE = 1
        self.FOR_LOOP_ITERATED_LIST = 2
        self.ITERATOR = 0
