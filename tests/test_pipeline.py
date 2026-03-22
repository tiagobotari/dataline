import unittest
from dataline import Pipeline, Operation


class AddOne(Operation):
    """Adds 1 to every element."""
    def process(self, data):
        return [x + 1 for x in data]


class MultiplyByTwo(Operation):
    """Multiplies every element by 2."""
    def process(self, data):
        return [x * 2 for x in data]


class Identity(Operation):
    """Returns data unchanged."""
    def process(self, data):
        return data


class TestPipeline(unittest.TestCase):

    def test_empty_pipeline_raises(self):
        pipe = Pipeline()
        with self.assertRaises(ValueError):
            pipe.process([1, 2, 3])

    def test_single_operation(self):
        pipe = Pipeline()
        pipe.add(AddOne())
        result, report = pipe.process([1, 2, 3])
        self.assertEqual(result, [2, 3, 4])
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["operation_name"], "AddOne")

    def test_chained_operations(self):
        pipe = Pipeline()
        pipe.add(AddOne())
        pipe.add(MultiplyByTwo())
        result, report = pipe.process([1, 2, 3])
        self.assertEqual(result, [4, 6, 8])
        self.assertEqual(len(report), 2)

    def test_verbose_mode(self):
        pipe = Pipeline(verbose=True)
        pipe.add(AddOne())
        result, report = pipe.process([0])
        self.assertEqual(result, [1])

    def test_report_contains_documentation(self):
        pipe = Pipeline()
        pipe.add(AddOne())
        _, report = pipe.process([1])
        self.assertEqual(report[0]["documentation"], "Adds 1 to every element.")

    def test_operation_number_increments(self):
        pipe = Pipeline()
        pipe.add(AddOne())
        pipe.add(MultiplyByTwo())
        self.assertEqual(pipe.operation_number, 2)

    def test_empty_list(self):
        pipe = Pipeline()
        pipe.add(AddOne())
        result, report = pipe.process([])
        self.assertEqual(result, [])
        self.assertEqual(len(report), 1)

    def test_single_element(self):
        pipe = Pipeline()
        pipe.add(AddOne())
        pipe.add(MultiplyByTwo())
        result, _ = pipe.process([5])
        self.assertEqual(result, [12])

    def test_identity_passthrough(self):
        pipe = Pipeline()
        pipe.add(Identity())
        data = [1, 2, 3]
        result, _ = pipe.process(data)
        self.assertEqual(result, data)

    def test_many_operations(self):
        pipe = Pipeline()
        for _ in range(10):
            pipe.add(AddOne())
        result, report = pipe.process([0])
        self.assertEqual(result, [10])
        self.assertEqual(len(report), 10)

    def test_verbose_propagates_to_added_operations(self):
        pipe = Pipeline(verbose=True)
        op = AddOne()
        self.assertFalse(op.verbose)
        pipe.add(op)
        self.assertTrue(op.verbose)

    def test_report_contains_custom_fields(self):
        class WithCustomReport(Operation):
            """Custom."""
            def process(self, data):
                self.report["custom_key"] = 42
                return data

        pipe = Pipeline()
        pipe.add(WithCustomReport())
        _, report = pipe.process([1])
        self.assertEqual(report[0]["custom_key"], 42)
        self.assertEqual(report[0]["operation_name"], "WithCustomReport")

    def test_dict_data(self):
        class AddKey(Operation):
            """Adds a key."""
            def process(self, data):
                data["new"] = True
                return data

        pipe = Pipeline()
        pipe.add(AddKey())
        result, _ = pipe.process({"a": 1})
        self.assertEqual(result, {"a": 1, "new": True})

    def test_string_data(self):
        class Upper(Operation):
            """Uppercase."""
            def process(self, data):
                return data.upper()

        pipe = Pipeline()
        pipe.add(Upper())
        result, _ = pipe.process("hello")
        self.assertEqual(result, "HELLO")


class TestNumpy(unittest.TestCase):
    """Tests with NumPy arrays (skipped if NumPy is not installed)."""

    @classmethod
    def setUpClass(cls):
        try:
            import numpy as np
            cls.np = np
        except ImportError:
            raise unittest.SkipTest("NumPy not installed")

    def test_numpy_array_operation(self):
        np = self.np

        class DoubleArray(Operation):
            """Doubles all values."""
            def process(self, data):
                return data * 2

        pipe = Pipeline()
        pipe.add(DoubleArray())
        result, report = pipe.process(np.array([1, 2, 3]))
        np.testing.assert_array_equal(result, np.array([2, 4, 6]))
        self.assertEqual(len(report), 1)

    def test_numpy_shape_report(self):
        np = self.np

        class AddColumn(Operation):
            """Adds a sum column."""
            def process(self, data):
                self.report["shape_before"] = data.shape
                data = np.c_[data, data[:, 0] + data[:, 1]]
                self.report["shape_after"] = data.shape
                return data

        data = np.array([[1, 2], [3, 4]])
        pipe = Pipeline()
        pipe.add(AddColumn())
        result, report = pipe.process(data)
        self.assertEqual(result.shape, (2, 3))
        self.assertEqual(report[0]["shape_before"], (2, 2))
        self.assertEqual(report[0]["shape_after"], (2, 3))

    def test_numpy_chained(self):
        np = self.np

        class Normalize(Operation):
            """Normalize to [0, 1]."""
            def process(self, data):
                return (data - data.min()) / (data.max() - data.min())

        class Round(Operation):
            """Round to 2 decimals."""
            def process(self, data):
                return np.round(data, 2)

        pipe = Pipeline()
        pipe.add(Normalize())
        pipe.add(Round())
        result, report = pipe.process(np.array([0, 50, 100]))
        np.testing.assert_array_equal(result, np.array([0.0, 0.5, 1.0]))
        self.assertEqual(len(report), 2)

    def test_numpy_empty_array(self):
        np = self.np

        class Identity(Operation):
            """Pass through."""
            def process(self, data):
                return data

        pipe = Pipeline()
        pipe.add(Identity())
        result, _ = pipe.process(np.array([]))
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
