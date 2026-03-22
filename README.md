# DataLine

A lightweight Python library for building data transformation pipelines. Define reusable operations, chain them together, and get structured reports on each transformation step.

## Features

- **Zero dependencies** -- pure Python, works with any data type
- **Chain of Responsibility pattern** -- compose operations into sequential pipelines
- **Built-in reporting** -- each operation can track metadata (e.g. shape changes, statistics)
- **Verbose mode** -- optional logging for debugging pipeline execution

## Installation

```bash
pip install dataline
```

Or install from source:

```bash
git clone https://github.com/tiagobotari/dataline.git
cd dataline
pip install .
```

## Quick Start

Create custom operations by subclassing `Operation` and implementing the `process` method:

```python
import numpy as np
import dataline as dl


class SumColumns(dl.Operation):
    """Sum columns at index 1 and 2 into a new column."""

    def process(self, data):
        self.report["shape_before"] = data.shape
        data = np.c_[data, data[:, 1] + data[:, 2]]
        self.report["shape_after"] = data.shape
        return data


data = np.array([[0, 1, 2], [1, 2, 2]])

pipe = dl.Pipeline()
pipe.add(SumColumns())
result, report = pipe.process(data)

print(result)
# [[0 1 2 3]
#  [1 2 2 4]]

print(report)
# [{'shape_before': (2, 3), 'shape_after': (2, 4), 'operation_name': 'SumColumns', ...}]
```

## Chaining Operations

Add multiple operations to process data in sequence:

```python
class DropFirstColumn(dl.Operation):
    """Remove the first column."""

    def process(self, data):
        return data[:, 1:]


pipe = dl.Pipeline(verbose=True)
pipe.add(SumColumns())
pipe.add(DropFirstColumn())
result, report = pipe.process(data)
```

Each operation receives the output of the previous one, and the final report contains one entry per operation.

## Running Tests

```bash
pytest
```

## License

MIT
