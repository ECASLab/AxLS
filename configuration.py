import os

from enum import Enum

from circuit import Circuit

class AlsMethod(str, Enum):
    CONSTANT_INPUTS = "inconst"
    CONSTANT_OUTPUTS = "outconst"
    PROBRUN = "probrun"
    SIGNIFICANCE = "significance"
    CCARVING = "ccarving"
    DECISION_TREE = "decision_tree"

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value

class Metric(str, Enum):
    MEAN_ERROR_DISTANCE = "med"
    WORST_CASE_ERROR = "wce"
    MEAN_RELATIVE_ERROR_DISTANCE = "mred"
    MEAN_SQUARED_ERROR_DISTANCE = "msed"
    ALS_TIME = "time"


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
    method : AlsMethod
        One of the supported methods. Can use the AlsMethod enum or one of the
        following string names: 'inconst', 'outconst', 'probrun',
        'significance', 'ccarving', or 'decision_tree'.

    circuit : Circuit
        A synthesized RTL circuit. See the circuit module.

    dataset : str
        Path to the dataset file.
        TODO: Document dataset file format.

    resynthesis : bool, default=False
        Whether to use resynthesis.

    error : float (0 < x <= 1)
        The maximum error threshold permitted. Required for iterative methods,
        like pruning methods or ML methods with resynthesis.

    max_iters : int, optional
        Maximum amount of iterations to execute. Used in iterative methods,
        like pruning methods or ML methods with resynthesis.

    max_depth : int
        Required for 'decision_tree'.

    one_tree_per_output : bool, default=False
        Used only by 'decision_tree' method.
        If True, uses a separate tree per output.
        If False, uses a single multi-output tree.

    show_progress : bool, default=False
        Whether to show simulation progress.
    """

    method: AlsMethod
    circuit: Circuit
    dataset: str
    resynthesis: bool
    error: float | None
    max_iters: int | None
    max_depth: int | None
    one_tree_per_output: bool
    show_progress: bool

    def __init__(
        self,
        method: AlsMethod,
        circuit: Circuit,
        dataset: str,
        resynthesis: bool,
        error: float | None,
        max_iters: int | None,
        max_depth: int | None,
        one_tree_per_output: bool,
        show_progress: bool,
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

        self.resynthesis = resynthesis
        self.error = _validate_error(error, self.method, self.resynthesis)
        self.max_iters = _validate_max_iters(max_iters, self.method, self.resynthesis)

        self.max_depth = _validate_max_depth(max_depth, self.method)
        self.one_tree_per_output = one_tree_per_output
        self.show_progress = show_progress

    def __repr__(self):
        fields = ", ".join(f"{key}={value!r}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"


def _validate_method(method: AlsMethod | str) -> AlsMethod:
    """
    Validates the synthesis method.

    If `method` is a string, tries to convert it to an AlsMethod enum.
    Raises a ValueError if the method name is invalid.

    Ensures consistency for downstream logic by enforcing enum usage.
    """
    if isinstance(method, str):
        try:
            method = AlsMethod(method)
        except ValueError:
            available_methods = ", ".join([method.value for method in AlsMethod])
            raise ValueError(
                f"{method} is not a valid {AlsMethod.__name__}. Available methods are: {available_methods}"
            )

    return method


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
