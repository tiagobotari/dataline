import abc, json


class BasePipeline(object):
    """BasePipeline"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, verbose=False):
        """
        self._next processing pipeline
        """
        self.verbose = verbose
        self._next = None
        self.operation_number = 0

    @abc.abstractmethod
    def _process(self, data):
        """

        :param data: input data
        :return: processed data
        """
        raise NotImplementedError

    def add(self, operation):
        """
        :param operation: operation object
        """
        if self.verbose:
            operation.verbose = self.verbose
        self.operation_number += 1
        if self._next is not None:
            self._next.add(operation)
        else:
            self._next = operation


class Pipeline(BasePipeline):

    def __init__(self, **kwargs):
        (super(Pipeline, self).__init__)(**kwargs)
        self.report = []

    def process(self, data):
        if not self._next:
            raise ValueError('Error, no transformation found')
        result, report = self._next._process(data, self.report)
        return (
         result, report)


class Operation(BasePipeline):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        (super(Operation, self).__init__)(**kwargs)
        self.report = {}

    def _process(self, data, report):
        if self.verbose:
            print('Starting Operation:', self.__class__.__name__)
        results = self.process(data)
        self.report.update(
            dict(
                operation_name=self.__class__.__name__
                , documentation=self.__class__.__doc__
                )
            )
        if self.verbose:
            self.print_report()
        report.append(self.report)
        if self._next:
            results, report = self._next._process(results, report)
        return (results, report)

    def print_report(self):
        report = self.report.copy()
        print('# Report:')
        print('#\t Operation name:', report.pop('operation_name', None))
        print('#\t Documentation:', report.pop('documentation', None))
        for key, content in report.items():
            print(f'\t {key} : {content}')
            print('--------------------------------')

        print()
        print('###############################')

    @staticmethod
    @abc.abstractmethod
    def process(data):
        """
        :param data: input data
        :return: processed data
        """
        raise NotImplementedError

