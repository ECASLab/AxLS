import os

from enum import Enum
from typing import override

from circuit import Circuit


class AlsMethod(str, Enum):
    CONSTANT_INPUTS = "inconst"
    CONSTANT_OUTPUTS = "outconst"
    PROBRUN = "probrun"
    SIGNIFICANCE = "significance"
    CCARVING = "ccarving"
    DECISION_TREE = "decision_tree"

    @override
    def __repr__(self):
        return self.value

    @override
    def __str__(self):
        return self.value


class Metric(str, Enum):
    HAMMING_DISTANCE = "hd"
    MEAN_ERROR_DISTANCE = "med"
    WORST_CASE_ERROR = "wce"
    MEAN_RELATIVE_ERROR_DISTANCE = "mred"
    MEAN_SQUARED_ERROR_DISTANCE = "msed"
    ALS_TIME = "time"
    AREA = "area"


    def to_user_friendly_display(self, value: float) -> str:
        """
        Formats the value to a user friendly string format for display.
        For example, the AREA metric is a percentage value, so it's formatted as
        such.
        """
        match self:
            # Percentage metrics
            case Metric.MEAN_RELATIVE_ERROR_DISTANCE | Metric.AREA:
                return f"{round(value*100, 2)}%"
            case Metric.ALS_TIME:
                return f"{round(value, 2)} s"
            # No special handling except rounding
            case _:
                return str(round(value, 2))



# List of iterative methods.
_ITERATIVE_METHODS = [
    AlsMethod.CONSTANT_INPUTS,
    AlsMethod.CONSTANT_OUTPUTS,
    AlsMethod.PROBRUN,
    AlsMethod.SIGNIFICANCE,
    AlsMethod.CCARVING,
]

# List of methods that aren't iterative but can be when doing resynthesis.
_ITERATIVE_METHODS_WITH_RESYNTHESIS = [AlsMethod.DECISION_TREE]


class ApproxSynthesisConfig:
    """
    Configuration class for running Approximate Logic Synthesis with different methods.

    Parameters
    ----------
    method : AlsMethod | str
        One of the supported methods. Can use the AlsMethod enum or one of the
        following string names: 'inconst', 'outconst', 'probrun',
        'significance', 'ccarving', or 'decision_tree'.

    circuit : Circuit
        A synthesized RTL circuit. See the circuit module.

    dataset : str
        Path to the dataset file.
        TODO: Document dataset file format.

    metrics : list[Metric | str]
        Metrics to calculate for the execution.
        The time metric is given in seconds, the area metric is given as a % of
        the area of the original circuit.

    resynthesis : bool, default=False
        Whether to use resynthesis.

    error : float (0 < x <= 1), optional
        The maximum error threshold permitted. Required for iterative methods,
        like pruning methods or ML methods with resynthesis.

        The error used is the Mean Relative Error Distance.

    max_iters : int, optional
        Maximum amount of iterations to execute. Used in iterative methods,
        like pruning methods or ML methods with resynthesis.

    max_depth : int, optional
        Required for 'decision_tree'.

    one_tree_per_output : bool, default=False
        Used only by 'decision_tree' method.
        If True, uses a separate tree per output.
        If False, uses a single multi-output tree.

    show_progress : bool, default=False
        Whether to show simulation progress.

    csv : str, optional
        Path to a file to save the output in csv format.
        If the file doesn't exist, it will be created with a header for the
        columns, if it exists it will be appended to.

        The output will be given as a single line with the following columns:
            method, circuit, resynthesis, error, max_iters, max_depth, one_tree_per_output, metric1, metric2, ...

        - bool values are stored as "True" or "False".
        - optional fields will just be left blank if not provided.
    """

    method: AlsMethod
    circuit: Circuit
    dataset: str
    metrics: list[Metric]
    resynthesis: bool
    error: float | None
    max_iters: int | None
    max_depth: int | None
    one_tree_per_output: bool
    show_progress: bool
    csv: str | None

    def __init__(
        self,
        method: AlsMethod | str,
        circuit: Circuit,
        dataset: str,
        metrics: list[Metric | str],
        resynthesis: bool = False,
        error: float | None = None,
        max_iters: int | None = None,
        max_depth: int | None = None,
        one_tree_per_output: bool = False,
        show_progress: bool = False,
        csv: str | None = None,
    ):
        """
        Instantiate and validate an ApproxSynthesisConfig.

        Raises
        ------
        ValueError
            If required parameters are missing or invalid.
        """
        self.method = _validate_method(method)
        self.circuit = circuit
        self.dataset = _validate_dataset(dataset)
        self.metrics = _validate_metrics(metrics)

        self.resynthesis = resynthesis
        self.error = _validate_error(error, self.method, self.resynthesis)
        self.max_iters = _validate_max_iters(max_iters, self.method, self.resynthesis)

        self.max_depth = _validate_max_depth(max_depth, self.method)
        self.one_tree_per_output = one_tree_per_output
        self.show_progress = show_progress
        self.csv = csv

    @override
    def __repr__(self):
        fields = ", ".join(f"{key}={value!r}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"

    def csv_columns(self) -> list[str]:
        """
        Returns the names of the columns used if exporting this config's
        execution to a CSV
        """
        columns = [
            "method",
            "circuit",
            "resynthesis",
            "error",
            "max_iters",
            "max_depth",
            "one_tree_per_output",
        ]
        for metric in self.metrics:
            columns.append(metric.value)

        return columns

    def csv_values(self, results: dict[Metric, float]) -> list[str]:
        """
        Returns the values of the columns if exporting this config's execution to
        a CSV row.
        A Results dict must be provided, it is assumed it contains the results
        for the metrics given to this config.
        """
        values = [
            self.method.value,
            self.circuit.topmodule,
            self.resynthesis,
            self.error,
            self.max_iters,
            self.max_depth,
            self.one_tree_per_output,
        ]

        for metric in self.metrics:
            values.append(results[metric])

        stringified_values = [
            str(value) if value is not None else "" for value in values
        ]

        return stringified_values


def _validate_method(method: AlsMethod | str) -> AlsMethod:
    """
    Validates the synthesis method.

    If `method` is a string, tries to convert it to an AlsMethod enum.
    Raises a ValueError if the method name is invalid.

    Ensures consistency for downstream logic by enforcing enum usage.
    """
    try:
        method = AlsMethod(method)
    except ValueError:
        available_methods = ", ".join([method.value for method in AlsMethod])
        raise ValueError(
            f"{method} is not a valid {AlsMethod.__name__}. Available methods are: {available_methods}"
        )

    return method


def _validate_metrics(metrics: list[str | Metric]) -> list[Metric]:
    """
    Validates the metrics.

    If a metric is given as a string, this functions tries to convert it to a
    Metric enum.
    Raises a ValueError if the metric name is invalid.

    Ensures consistency for downstream logic by enforcing enum usage.
    """

    result_metrics: list[Metric] = []

    for metric in metrics:
        try:
            result_metrics.append(Metric(metric))
        except ValueError:
            available_metrics = ", ".join([metric.value for metric in Metric])
            raise ValueError(
                f"{metric} is not a valid {Metric.__name__}. Available metrics are: {available_metrics}"
            )

    return result_metrics


def _validate_dataset(
    dataset: str,
) -> str:
    """
    Ensures the dataset file exists.
    TODO: We could maybe validate that the values match up with the circuit's inputs.

    Raises a ValueError if the dataset file is missing or doesn't match the
    circuit inputs.
    """
    if not os.path.isfile(dataset):
        raise ValueError(f"Dataset file not found: {dataset}..")

    return dataset


def _validate_error(
    error: float | None,
    method: AlsMethod,
    resynthesis: bool,
) -> float | None:
    """
    Validates 'error'.

    Required for:
    - all iterative methods
    - methods that become iterative with resynthesis, like decision_tree

    Raises ValueError if missing in those cases.
    """
    if method in _ITERATIVE_METHODS:
        if error is None:
            raise ValueError(f"'error' is required for method {method}")
    elif (
        method in _ITERATIVE_METHODS_WITH_RESYNTHESIS and resynthesis and error is None
    ):
        raise ValueError(f"'error' is required for method {method} with resynthesis")

    return error


def _validate_max_iters(
    max_iters: int | None, method: AlsMethod, resynthesis: bool
) -> int | None:
    """
    Validates 'max_iters'.

    Required for iterative methods.
    Raises ValueError if missing in that case.
    """

    if method in _ITERATIVE_METHODS:
        if max_iters is None:
            raise ValueError(f"'max_iters' is required for method {method}")
    if (
        method in _ITERATIVE_METHODS_WITH_RESYNTHESIS
        and resynthesis
        and max_iters is None
    ):
        raise ValueError(f"'max_iters' is required for {method} with resynthesis")


def _validate_max_depth(
    max_depth: int | None,
    method: AlsMethod,
) -> int | None:
    """
    Validates 'max_depth' for decision trees.

    Ensures it is provided for the 'decision_tree' method and aligns with
    the number of circuit files if given as a list.

    Ensures values are valid:
    - int: must be > 1

    Raises ValueError if missing or mismatched.
    """
    if method == AlsMethod.DECISION_TREE:
        if max_depth is None:
            raise ValueError(f"'max_depth' is required for method f{method}.")
        else:
            if max_depth <= 1:
                raise ValueError("max_depth must be > 1")

            return max_depth
