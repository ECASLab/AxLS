from typing import List
import os

from enum import Enum


class AlsMethod(str, Enum):
    CONSTANT_INPUTS = "inconst"
    CONSTANT_OUTPUTS = "outconst"
    PROBRUN = "probrun"
    SIGNIFICANCE = "significance"
    CCARVING = "ccarving"
    DECISION_TREE = "decision_tree"


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

    circuit_file : str | List[str]
        Path(s) to the Verilog circuit file(s).

    dataset_file : str | List[str]
        Path(s) to the dataset file(s).

        If multiple circuits were specified with `circuit_file`, this can be
        given as a list which must match the `circuit_file` list length.
        Each dataset will be used with each corresponding circuit.

    generate_dataset : str | int | float | List[str | int | float], optional
        If specified, the dataset file(s) given with dataset_file will be
        generated on the spot. Overwriting any existing file(s).

        Rule(s) to generate dataset. Can be:
        - 'exhaustive' (only for circuits with number of inputs <= 32)
        - an integer number of inputs
        - a float percentage (0 < x <= 1)

        If multiple datasets were specified with `dataset_file`, this option can
        be given as a list which must match the `dataset_file` list length.
        Each dataset will be generated with the corresponding settings.

    dataset_fraction : int | float | List[int | float], optional
        Subset of dataset to use. Cannot be used with `generate_dataset`.

        Can be given as:
        - an integer number of inputs (lower than dataset size)
        - a float percentage (0 < x <= 1)

        If multiple datasets were specified with `dataset_file`, this option
        can be given as a list which must match the `dataset_file` list length.
        Each dataset will be generated with the corresponding settings.

    resynthesis : bool, default=False
        Whether to use resynthesis.

    error_threshold : float (0 < x <= 1)
        The maximum error threshold permitted. Required for iterative methods,
        like pruning methods or ML methods with resynthesis.

    max_iters : int, optional
        Maximum amount of iterations to execute. Used in iterative methods,
        like pruning methods or ML methods with resynthesis.

    save_file : str, optional
        Path to file where configuration and progress of the run is saved.

    continue_from_save : bool, default=False
        Whether to continue from a saved file. If True, `save_file` option must
        be provided. If the file doesn't exist, a new run will be started.

    max_depth : int | List[int]
        Required for 'decision_tree'. Can be a single int or list if multiple
        circuits are specified. In which case the list must match the
        `circuit_file` list length. Each circuit will use the corresponding max
        depth for its decision tree.

    one_tree_per_output : bool, default=False
        Used only by 'decision_tree' method.
        If True, uses a separate tree per output.
        If False, uses a single multi-output tree.

    show_tb_progress : bool, default=False
        Whether to show simulation progress.
    """

    # After instantiation/validation the method is always turned into an
    # AlsMethod and anything that can be a list is turned into a list. For ease
    # of use of this struct in the runner code.
    method: AlsMethod
    circuit_file: List[str]
    dataset_file: List[str]
    generate_dataset: List[str | int | float] | None
    dataset_fraction: List[int | float] | None
    resynthesis: bool
    error_threshold: float | None
    max_iters: int | None
    save_file: str | None
    continue_from_save: bool
    max_depth: List[int] | None
    one_tree_per_output: bool
    show_tb_progress: bool

    def __init__(
        self,
        method: AlsMethod | str,
        circuit_file: str | List[str],
        dataset_file: str | List[str],
        generate_dataset: str | int | float | List[str | int | float] | None = None,
        dataset_fraction: int | float | List[int | float] | None = None,
        resynthesis: bool = False,
        error_threshold: float | None = None,
        max_iters: int | None = None,
        save_file: str | None = None,
        continue_from_save: bool = False,
        max_depth: int | List[int] | None = None,
        one_tree_per_output: bool = False,
        show_tb_progress: bool = False,
    ):
        """
        Instantiate and validate an ApproxSynthesisConfig.

        Raises
        ------
        ValueError
            If required parameters are missing or invalid.
        """
        self.method = _validate_method(method)
        self.circuit_file = _validate_circuit_files(circuit_file)
        self.dataset_file = _validate_dataset_files(
            dataset_file, self.circuit_file, generate_dataset
        )

        _validate_dataset_fraction_vs_generate_exclusivity(
            generate_dataset, dataset_fraction
        )

        self.generate_dataset = _validate_generate_dataset(
            generate_dataset, self.dataset_file
        )
        self.dataset_fraction = _validate_dataset_fraction(
            dataset_fraction, self.dataset_file
        )

        self.resynthesis = resynthesis
        self.error_threshold = _validate_error_threshold(
            error_threshold, self.method, self.resynthesis
        )
        self.max_iters = _validate_max_iters(max_iters, self.method, self.resynthesis)
        self.max_depth = _validate_max_depth(max_depth, self.method, self.circuit_file)
        self.save_file = _validate_save_file(save_file, continue_from_save)
        self.continue_from_save = continue_from_save
        self.one_tree_per_output = one_tree_per_output
        self.show_progress = show_tb_progress

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


def _validate_circuit_files(circuits: str | List[str]) -> List[str]:
    """
    Validates the existence of circuit files.

    Checks if each file path in `circuit_file` exists. If not, raises a ValueError.
    Ensures input Verilog files are valid for further processing.
    """
    circuits = circuits if isinstance(circuits, list) else [circuits]
    for circuit in circuits:
        if not os.path.isfile(circuit):
            raise ValueError(f"Circuit file does not exist: {circuit}")

    return circuits


def _validate_dataset_files(
    dataset_files: str | List[str],
    circuit_files: List[str],
    generate_dataset: str | int | float | List[str | int | float] | None,
) -> List[str]:
    """
    Validates dataset files.

    Ensures each dataset file exists, unless 'generate_dataset' is set.

    Uses `_ensure_length_match` to validate correspondence with circuit files.
    Raises a ValueError if any required dataset file is missing.
    """
    dataset_files = _ensure_length_match(
        dataset_files, circuit_files, "dataset_file", "circuit_file"
    )
    if generate_dataset is None:
        for f in dataset_files:
            if not os.path.isfile(f):
                raise ValueError(
                    f"Dataset file not found: {f}. Use 'generate_dataset' or provide a valid file."
                )
    return dataset_files


def _validate_dataset_fraction_vs_generate_exclusivity(
    generate_dataset: str | int | float | List[str | int | float] | None,
    dataset_fraction: int | float | List[int | float] | None,
):
    """
    Ensures mutual exclusivity between 'generate_dataset' and 'dataset_fraction'.

    Both fields are incompatible; only one may be provided.
    Raises a ValueError if both are given.
    """
    if generate_dataset is not None and dataset_fraction is not None:
        raise ValueError(
            "Cannot specify both 'generate_dataset' and 'dataset_fraction'."
        )


def _validate_generate_dataset(
    generate_dataset: str | int | float | List[str | int | float] | None,
    dataset_files: List[str],
) -> List[str | int | float] | None:
    """
    Validates 'generate_dataset' parameters.

    Ensures that each generation rule is valid:
    - str: must be 'exhaustive'
    - int: must be > 0
    - float: must be in (0, 1]

    Uses `_ensure_length_match` to align with dataset files.
    Raises ValueError for invalid values.
    """
    if generate_dataset is not None:
        gens = _ensure_length_match(
            generate_dataset,
            dataset_files,
            "generate_dataset",
            "dataset_file",
        )
        for g in gens:
            if isinstance(g, str):
                if g != "exhaustive":
                    raise ValueError(f"Invalid generate_dataset string: {g}")
                # TODO: Check number of inputs in circuit (must be <= 32)
            elif isinstance(g, int):
                if g <= 0:
                    raise ValueError("Integer generate_dataset must be > 0")
                # TODO: Check it's <= max input count of the circuit
            elif isinstance(g, float):
                if not (0 < g <= 1):
                    raise ValueError(
                        "Percentage generate_dataset must be between 0 and 1."
                    )
            else:
                raise ValueError(f"Invalid generate_dataset value: {g}")
        return gens


def _validate_dataset_fraction(
    dataset_fraction: int | float | List[int | float] | None,
    dataset_files: List[str],
) -> List[int | float] | None:
    """
    Validates 'dataset_fraction'.

    Ensures values are valid:
    - int: must be > 0
    - float: must be in (0, 1]

    Uses `_ensure_length_match` to align with dataset files.
    Raises ValueError for out-of-range values.
    """
    if dataset_fraction is not None:
        fracs = _ensure_length_match(
            dataset_fraction,
            dataset_files,
            "dataset_fraction",
            "dataset_file",
        )
        for f in fracs:
            if isinstance(f, int) and f <= 0:
                raise ValueError("dataset_fraction as int must be > 0")
            elif isinstance(f, float) and not (0 < f <= 1):
                raise ValueError(
                    "dataset_fraction as percentage must be between 0 and 1"
                )
            # TODO: Check dataset size to ensure integer fraction < full dataset
        return fracs


def _validate_error_threshold(
    error_threshold: float | None,
    method: AlsMethod,
    resynthesis: bool,
) -> float | None:
    """
    Validates 'error_threshold'.

    Required for:
    - all iterative methods
    - methods that become iterative with resynthesis, like decision_tree

    Raises ValueError if missing in those cases.
    """
    if method in _ITERATIVE_METHODS:
        if error_threshold is None:
            raise ValueError(f"'error_threshold' is required for method {method}")
    elif (
        method in _ITERATIVE_METHODS_WITH_RESYNTHESIS
        and resynthesis
        and error_threshold is None
    ):
        raise ValueError(
            f"'error_threshold' is required for method {method} with resynthesis"
        )

    return error_threshold


def _validate_max_iters(
    max_iters: int | None, method: AlsMethod, resynthesis: bool
) -> int | None:
    """
    Validates 'max_iters'.

    Required only for methods that become iterative under resynthesis,
    like decision_tree; because they might never reach the error threshold.
    Raises ValueError if missing in that case.
    """
    if (
        method in _ITERATIVE_METHODS_WITH_RESYNTHESIS
        and resynthesis
        and max_iters is None
    ):
        raise ValueError(f"'max_iters' is required for {method} with resynthesis")


def _validate_max_depth(
    max_depth: int | List[int] | None, method: AlsMethod, circuit_files: List[str]
):
    """
    Validates 'max_depth' for decision trees.

    Ensures it is provided for the 'decision_tree' method and aligns with
    the number of circuit files if given as a list.
    Raises ValueError if missing or mismatched.
    """
    if method == AlsMethod.DECISION_TREE:
        if max_depth is None:
            raise ValueError(f"'max_depth' is required for method f{method}.")
        else:
            _ensure_length_match(max_depth, circuit_files, "max_depth", "circuit_file")


def _validate_save_file(save_file: str | None, continue_from_save: bool) -> str | None:
    """
    Validates parameters for continuing from a saved file.

    Ensures 'save_file' is provided and exists on disk when
    'continue_from_save' is True. Raises ValueError otherwise.
    """
    if continue_from_save:
        if save_file is None:
            raise ValueError("To continue from save, 'save_file' must be provided.")
        if not os.path.isfile(save_file):
            raise ValueError(
                f"To continue from save, 'save_file' must exist: {save_file}"
            )

    return save_file


def _ensure_length_match[T: str | int | float](
    values: T | List[T],
    ref_values: List[str],
    field_name: str,
    ref_name: str,
) -> List[T]:
    """
    Ensures list parameters match reference list length.

    Converts scalar to list and compares length if both are lists.
    Raises ValueError if mismatched or list is given with scalar reference.

    When converting scalar to list, the list returned contains N copies of the
    scalar value, where N is the length of the reference list.
    This is done so that the config object ends up with only lists that all are
    of equal length, for easy handling in the runner code.

    Parameters
    ----------
    values : Any
        Parameter to validate (scalar or list).
    ref_values : Any
        Reference parameter (scalar or list).
    field_name : str
        Name of the field being validated (for error messages).
    ref_name : str
        Name of the reference field (for error messages).

    Returns
    -------
    List[Any]
        The validated values, always as a list.
    """
    if isinstance(values, list):
        if len(values) != len(ref_values):
            raise ValueError(
                f"'{field_name}' length ({len(values)}) must match {ref_name} count ({len(ref_values)})"
            )
        return values
    else:
        value: T = values
        return [value for _ in ref_values]
