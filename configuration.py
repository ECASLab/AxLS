import os

from enum import Enum
from typing import override

from circuit import Circuit


class AlsMethod(str, Enum):
    CONSTANT_INPUTS = "inconst"
    CONSTANT_OUTPUTS = "outconst"
    PROBPRUN = "probprun"
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
                return f"{round(value * 100, 2)}%"
            case Metric.ALS_TIME:
                return f"{round(value, 2)} s"
            # No special handling except rounding
            case _:
                return str(round(value, 2))

    def is_error_metric(self) -> bool:
        # This set should contain all the Metrics that are related to
        # approximation errors.
        return self in {
            Metric.HAMMING_DISTANCE,
            Metric.MEAN_ERROR_DISTANCE,
            Metric.WORST_CASE_ERROR,
            Metric.MEAN_RELATIVE_ERROR_DISTANCE,
            Metric.MEAN_SQUARED_ERROR_DISTANCE,
        }


# List of iterative methods.
_ITERATIVE_METHODS = [
    AlsMethod.CONSTANT_INPUTS,
    AlsMethod.CONSTANT_OUTPUTS,
    AlsMethod.PROBPRUN,
    AlsMethod.SIGNIFICANCE,
    AlsMethod.CCARVING,
]


class ApproxSynthesisConfig:
    """
    Configuration class for running Approximate Logic Synthesis with different methods.

    Parameters
    ----------
    method : AlsMethod | str
        One of the supported methods. Can use the AlsMethod enum or one of the
        following string names: 'inconst', 'outconst', 'probprun',
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
        i.e. pruning methods.

        The error used is the Mean Relative Error Distance.

    validation : float (0 <= x < 1), optional
        Specifies the proportion of the input dataset to be allocated to the
        validation set.

        If provided, the dataset will be split into a validation set and a test
        set. For example, a value of 0.2 means 20% of the dataset will be used
        for validation, while 80% will be used for testing during ALS. This helps
        assess whether the generated solution generalizes well to unseen circuit
        inputs.

        A value of 0 indicates that the full dataset will be used for training,
        similar to not providing this parameter. However, it can be useful when
        generating csv data because the columns will be formatted to align with
        other circuits that are using a validation set.

    max_iters : int, optional
        Maximum amount of iterations to execute. Used in iterative methods,
        i.e. pruning methods.

    prunes_per_iteration : int, default=1
        Number of pruning operations to perform per iteration during ALS.
        Increasing this value can speed up pruning-based methods by reducing the
        number of iterations. It doesn't affect ccarving since it already prunes
        multiple nodes per iteration. If the resulting circuit exceeds the error
        threshold, the algorithm backtracks to the last valid state before
        continuing. If this parameter is too large, backtracking may take longer
        than the initial search, especially for small circuits.

    max_depth : int, optional
        Required for 'decision_tree'.

    one_tree_per_output : bool, default=False
        Used only by 'decision_tree' method.
        If True, uses a separate tree per output.
        If False, uses a single multi-output tree.

    output_significances: list[int]
        List of significances of the circuit outputs. Should match the number of
        output bits of the circuit.

        If not provided a significance of 2**i will be assumed, where i is the
        index of the output bit. (LSB has less significance that MSB.)

        Used by the 'significance' and 'ccarving' methods.

    show_progress : bool, default=False
        Whether to show simulation progress.

    csv : str, optional
        Path to a file for saving the output in CSV format. If the file does not
        exist, it will be created with a header; if it exists, the output will be
        appended.

        The output will be given as a single line with the following columns:
            method, circuit, resynthesis, error, max_depth, one_tree_per_output, metric1, metric2, ...

        If the 'validation' option is given, the metrics will include validation results, formatted as:

            metric1, v_metric1, metric2, v_metric2, ...

        Where 'v_' indicates the metric's result on the validation set. This
        applies only to error metrics.

        - bool values are stored as "True" or "False".
        - optional fields (error, max_depth, one_tree_per_output) will
        just be left blank if not provided.
    """

    # TODO: the configuration options included in the csv: resynthesis, error,
    # max_depth and one_tree_per_output; were chosen arbitrarily and are not
    # necessarily more interesting than other options not included. Perhaps the
    # configuration options included in the CSV should also be configurable, or
    # we should include any options that are not None, or we should always
    # include every single possible option and metric in the csv, even those
    # not specified.

    method: AlsMethod
    circuit: Circuit
    dataset: str
    metrics: list[Metric]
    resynthesis: bool
    error: float | None
    validation: float | None
    max_iters: int | None
    prunes_per_iteration: int
    max_depth: int | None
    one_tree_per_output: bool
    output_significances: list[int] | None
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
        validation: float | None = None,
        max_iters: int | None = None,
        prunes_per_iteration: int = 1,
        max_depth: int | None = None,
        one_tree_per_output: bool = False,
        output_significances: list[int] | None = None,
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
        self.error = _validate_error(error, self.method)
        self.validation = _validate_validation(validation)
        self.max_iters = max_iters
        self.prunes_per_iteration = _validate_prunes_per_iteration(prunes_per_iteration)

        self.max_depth = _validate_max_depth(max_depth, self.method)
        self.one_tree_per_output = one_tree_per_output
        self.output_significances = _validate_output_significances(
            self.circuit, output_significances
        )
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
            "max_depth",
            "one_tree_per_output",
        ]
        for metric in self.metrics:
            columns.append(metric.value)
            if self.validation is not None and metric.is_error_metric():
                columns.append(f"v_{metric.value}")

        return columns

    def csv_values(
        self,
        results: dict[Metric, float],
        validation_results: None | dict[Metric, float],
    ) -> list[str]:
        """
        Returns the values of the columns if exporting this config's execution to
        a CSV row.
        A Results dict must be provided, it is assumed it contains the results
        for the metrics given to this config.
        A validation Results dict can be provided, if it is, it's assumed it
        contains the results for the error metrics provided to this config.
        """
        values = [
            self.method.value,
            self.circuit.topmodule,
            self.resynthesis,
            self.error,
            self.max_depth,
            self.one_tree_per_output,
        ]

        for metric in self.metrics:
            values.append(results[metric])
            if validation_results is not None and metric.is_error_metric():
                # We use `get` because maybe the metric might not be in the dict
                # if the 'validation' option was given with a value of 0
                values.append(validation_results.get(metric, None))

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
) -> float | None:
    """
    Validates 'error'.

    Required for:
    - all iterative methods

    Raises ValueError if missing in those cases.
    """
    if method in _ITERATIVE_METHODS:
        if error is None:
            raise ValueError(f"'error' is required for method {method}")

    return error


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
            raise ValueError(f"'max_depth' is required for method {method}.")
        else:
            if max_depth <= 1:
                raise ValueError("max_depth must be > 1")

            return max_depth


def _validate_validation(validation: float | None) -> float | None:
    """
    Validates the 'validation' parameter.

    Ensures that the value is a float within the range (0, 1].
    If the value is None, it is considered valid and returned as is.

    Raises ValueError if the value is not in the specified range.
    """
    if validation is not None:
        if not (0 <= validation < 1.0):
            raise ValueError(
                "'validation' value must be a float in the range 0 <= x < 1."
            )

    return validation


def _validate_output_significances(
    circuit: Circuit,
    output_significances: list[int] | None,
) -> list[int] | None:
    """
    Validates 'output_significances'.

    Ensures that if provided it matches in length the circuit's outputs.

    Raises ValueError if mismatched.
    """
    if output_significances is not None:
        if len(output_significances) != len(circuit.outputs):
            raise ValueError(
                f"'output_significances' length ({len(output_significances)}) does not match the amount of circuit outputs ({len(circuit.outputs)})."
            )

    return output_significances


def _validate_prunes_per_iteration(prunes_per_iteration: int) -> int:
    if prunes_per_iteration < 1:
        raise ValueError("prunes_per_iteration must be at least 1.")
    return prunes_per_iteration
