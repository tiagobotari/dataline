import abc
import logging
from typing import Any, List, Tuple

logger = logging.getLogger(__name__)


class Pipeline:
    """Entry point for building and executing a data transformation pipeline.

    A ``Pipeline`` manages an ordered list of operations. Operations are
    added via :meth:`add` and executed sequentially via :meth:`process`.

    Example::

        pipe = Pipeline(verbose=True)
        pipe.add(MyOperation())
        result, report = pipe.process(raw_data)

    Attributes:
        verbose: When True, enables detailed logging during pipeline execution.
        operation_number: Total count of operations in the pipeline.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._operations: List["Operation"] = []

    @property
    def operation_number(self) -> int:
        return len(self._operations)

    def add(self, operation: "Operation") -> None:
        """Appends an operation to the end of the pipeline.

        Args:
            operation: An ``Operation`` instance to append. If ``verbose``
                is enabled on the pipeline, it will also be enabled on the
                appended operation.
        """
        if self.verbose:
            operation.verbose = True
        self._operations.append(operation)

    def process(self, data: Any) -> Tuple[Any, List[dict]]:
        """Runs input data through all operations in order.

        Each operation transforms the data and produces a report dictionary.
        Reports are freshly generated on every call, so pipelines are reusable.

        Args:
            data: The input data to be transformed. Can be any type
                accepted by the first operation in the chain (e.g. a
                NumPy array, a pandas DataFrame, or a plain list).

        Returns:
            A two-element tuple containing:
                - The final transformed data after all operations.
                - A list of report dictionaries, one per operation,
                  each containing at least ``operation_name`` and
                  ``documentation`` keys.

        Raises:
            ValueError: If no operations have been added to the pipeline.
        """
        if not self._operations:
            raise ValueError("No operations added to the pipeline.")

        report: List[dict] = []
        for operation in self._operations:
            data, step_report = operation._execute(data)
            report.append(step_report)

        return data, report


class Operation(abc.ABC):
    """Abstract base class for a single data transformation step.

    Subclass this and implement :meth:`process` to define a transformation.
    Custom report fields can be set by writing to ``self.report`` inside
    :meth:`process`.

    Example::

        class Normalize(Operation):
            \"\"\"Normalize values to [0, 1] range.\"\"\"

            def process(self, data):
                min_val, max_val = min(data), max(data)
                self.report["min"] = min_val
                self.report["max"] = max_val
                return [(x - min_val) / (max_val - min_val) for x in data]

    Attributes:
        report: Dictionary of metadata collected during the current execution.
            Automatically includes ``operation_name`` and ``documentation``;
            subclasses may add custom keys.
    """

    def __init__(self):
        self.verbose: bool = False
        self.report: dict = {}

    def _execute(self, data: Any) -> Tuple[Any, dict]:
        """Executes this operation and returns the result with a fresh report.

        This is an internal method called by the pipeline. It resets the
        report, wraps the user-defined :meth:`process`, and records metadata.

        Args:
            data: Input data to be transformed by this operation.

        Returns:
            A two-element tuple containing:
                - The transformed data.
                - A report dictionary with operation metadata and any
                  custom fields set during :meth:`process`.
        """
        self.report = {}
        if self.verbose:
            logger.info("Starting Operation: %s", self.__class__.__name__)
        result = self.process(data)
        self.report.update({
            "operation_name": self.__class__.__name__,
            "documentation": self.__class__.__doc__,
        })
        if self.verbose:
            self._log_report()
        return result, self.report

    def _log_report(self) -> None:
        """Logs the operation's report using the module logger.

        Displays the operation name and documentation first, followed by
        any custom fields added by the subclass during :meth:`process`.
        """
        report = self.report.copy()
        lines = [
            "Report:",
            f"  Operation name: {report.pop('operation_name', None)}",
            f"  Documentation: {report.pop('documentation', None)}",
        ]
        for key, content in report.items():
            lines.append(f"  {key}: {content}")
        logger.info("\n".join(lines))

    @abc.abstractmethod
    def process(self, data: Any) -> Any:
        """Transforms the input data. Must be implemented by subclasses.

        This is the core method where transformation logic lives. Use
        ``self.report`` to record any metadata about the transformation
        (e.g. shape changes, statistics, validation results).

        Args:
            data: The input data to transform. The expected type depends
                on the specific operation and the pipeline's data flow.

        Returns:
            The transformed data, which will be passed to the next
            operation in the chain or returned as the final result.
        """
        raise NotImplementedError
