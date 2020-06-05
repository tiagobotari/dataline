import numpy as np
import dataline as dl

class SumColsOneTwo(dl.Operation):
    """
    Perform the sum of index 1 with 2 and put the
    result in a new col. 
    """
    def process(self, data):
        data[:, :-1] = data[:, 1] + data[:, 2]
        self.report = {'result': 'Sum performed.'}
        return data

data = np.array([[0, 1, 2], [1, 2, 2]])

pipe = dl.Pipeline()
pipe.add(SumColsOneTwo())
data, report = pipe.process(data)
print(report)
print()
print(data)
