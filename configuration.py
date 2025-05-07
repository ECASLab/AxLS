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
    method : AlsMethod | str
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

    def __init__(
        self,
        method: str,
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
        self.method = method
        self.circuit_file = circuit_file
        self.dataset_file = dataset_file
        self.generate_dataset = generate_dataset
        self.dataset_fraction = dataset_fraction
        self.resynthesis = resynthesis
        self.error_threshold = error_threshold
        self.max_iters = max_iters
        self.save_file = save_file
        self.continue_from_save = continue_from_save
        self.max_depth = max_depth
        self.one_tree_per_output = one_tree_per_output
        self.show_progress = show_tb_progress
        validate_config(self)


def validate_config(config: ApproxSynthesisConfig):
    """
    Validates the given ApproxSynthesisConfig. For more details on how each
    parameter is checked, refer to the ApproxSynthesisConfig docs or to each
    `_validate...` function's docs.

    Raises
    ------
    ValueError
        If required parameters are missing or invalid.
    """

    _validate_method(config)
    _validate_circuit_files(config)
    _validate_dataset_files(config)
    _validate_dataset_vs_generate_exclusivity(config)
    _validate_generate_dataset(config)
    _validate_dataset_fraction(config)
    _validate_error_threshold(config)
    _validate_max_iters(config)
    _validate_max_depth(config)
    _validate_continue_from_save(config)


def _validate_method(config: ApproxSynthesisConfig):
    """
    Validates the synthesis method.

    If `method` is a string, tries to convert it to an AlsMethod enum.
    Raises a ValueError if the method name is invalid.

    Ensures consistency for downstream logic by enforcing enum usage.
    """
    if isinstance(config.method, str):
        try:
            config.method = AlsMethod(config.method)
        except ValueError:
            available_methods = ", ".join([method.value for method in AlsMethod])
            raise ValueError(
                f"{config.method} is not a valid {AlsMethod.__name__}. Available methods are: {available_methods}"
            )


def _validate_circuit_files(config: ApproxSynthesisConfig):
    """
    Validates the existence of circuit files.

    Checks if each file path in `circuit_file` exists. If not, raises a ValueError.
    Ensures input Verilog files are valid for further processing.
    """
    circuits = config.circuit_file
    circuits = circuits if isinstance(circuits, list) else [circuits]
    for circuit in circuits:
        if not os.path.isfile(circuit):
            raise ValueError(f"Circuit file does not exist: {circuit}")


def _validate_dataset_files(config: ApproxSynthesisConfig):
    """
    Validates dataset files.

    Ensures each dataset file exists, unless 'generate_dataset' is set.

    Uses `_ensure_length_match` to validate correspondence with circuit files.
    Raises a ValueError if any required dataset file is missing.
    """
    dataset_files = _ensure_length_match(
        config.dataset_file, config.circuit_file, "dataset_file", "circuit_file"
    )
    if config.generate_dataset is None:
        for f in dataset_files:
            if not os.path.isfile(f):
                raise ValueError(
                    f"Dataset file not found: {f}. Use 'generate_dataset' or provide a valid file."
                )


def _validate_dataset_vs_generate_exclusivity(config: ApproxSynthesisConfig):
    """
    Ensures mutual exclusivity between 'generate_dataset' and 'dataset_fraction'.

    Both fields are incompatible; only one may be provided.
    Raises a ValueError if both are given.
    """
    if config.generate_dataset is not None and config.dataset_fraction is not None:
        raise ValueError(
            "Cannot specify both 'generate_dataset' and 'dataset_fraction'."
        )


def _validate_generate_dataset(config: ApproxSynthesisConfig):
    """
    Validates 'generate_dataset' parameters.

    Ensures that each generation rule is valid:
    - str: must be 'exhaustive'
    - int: must be > 0
    - float: must be in (0, 1]

    Uses `_ensure_length_match` to align with dataset files.
    Raises ValueError for invalid values.
    """
    if config.generate_dataset is not None:
        gens = _ensure_length_match(
            config.generate_dataset,
            config.dataset_file,
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


def _validate_dataset_fraction(config: ApproxSynthesisConfig):
    """
    Validates 'dataset_fraction'.

    Ensures values are valid:
    - int: must be > 0
    - float: must be in (0, 1]

    Uses `_ensure_length_match` to align with dataset files.
    Raises ValueError for out-of-range values.
    """
    if config.dataset_fraction is not None:
        fracs = _ensure_length_match(
            config.dataset_fraction,
            config.dataset_file,
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


def _validate_error_threshold(config: ApproxSynthesisConfig):
    """
    Validates 'error_threshold'.

    Required for:
    - all iterative methods
    - methods that become iterative with resynthesis, like decision_tree

    Raises ValueError if missing in those cases.
    """
    if config.method in _ITERATIVE_METHODS:
        if config.error_threshold is None:
            raise ValueError(
                f"'error_threshold' is required for method {config.method}"
            )
    elif (
        config.method in _ITERATIVE_METHODS_WITH_RESYNTHESIS
        and config.resynthesis
        and config.error_threshold is None
    ):
        raise ValueError(
            f"'error_threshold' is required for method {config.method} with resynthesis"
        )


def _validate_max_iters(config: ApproxSynthesisConfig):
    """
    Validates 'max_iters'.

    Required only for methods that become iterative under resynthesis,
    like decision_tree; because they might never reach the error threshold.
    Raises ValueError if missing in that case.
    """
    if (
        config.method in _ITERATIVE_METHODS_WITH_RESYNTHESIS
        and config.resynthesis
        and config.max_iters is None
    ):
        raise ValueError(
            f"'max_iters' is required for {config.method} with resynthesis"
        )


def _validate_max_depth(config: ApproxSynthesisConfig):
    """
    Validates 'max_depth' for decision trees.

    Ensures it is provided for the 'decision_tree' method and aligns with
    the number of circuit files if given as a list.
    Raises ValueError if missing or mismatched.
    """
    if config.method == AlsMethod.DECISION_TREE:
        if config.max_depth is None:
            raise ValueError(f"'max_depth' is required for method f{config.method}.")
        else:
            _ensure_length_match(
                config.max_depth, config.circuit_file, "max_depth", "circuit_file"
            )


def _validate_continue_from_save(config: ApproxSynthesisConfig):
    """
    Validates parameters for continuing from a saved file.

    Ensures 'save_file' is provided and exists on disk when
    'continue_from_save' is True. Raises ValueError otherwise.
    """
    if config.continue_from_save:
        if config.save_file is None:
            raise ValueError("To continue from save, 'save_file' must be provided.")
        if not os.path.isfile(config.save_file):
            raise ValueError("To continue from save, 'save_file' must exist.")


def _ensure_length_match(values, ref_values, field_name, ref_name):
    """
    Ensures list parameters match reference list length.

    Converts scalar to list and compares length if both are lists.
    Raises ValueError if mismatched or list is given with scalar reference.

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
        if isinstance(ref_values, list):
            if len(values) != len(ref_values):
                raise ValueError(
                    f"'{field_name}' length ({len(values)}) must match {ref_name} count ({len(ref_values)})"
                )
        else:
            raise ValueError(
                f"'{field_name}' can't be given as a list if {ref_name} isn't a list."
            )
        return values
    else:
        return [values]
