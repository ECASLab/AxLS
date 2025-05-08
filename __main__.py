import argparse
from typing import List
from circuit import Circuit
from configuration import ApproxSynthesisConfig, AlsMethod, Metric

# The tech library is hardcoded for the following reasons:
# - Ease of use: This way users don't have to provide a tech library which most
#                of the time would be this same one.
# - Tool limitations:
#   - AxLS only provides this tech library.
#   - The Circuit class accepts a tech library "name" and assumes a .v and .lib
#     files by that name in the templates/ directory of AxLS exist.
#   - If we want to let users provide custom tech libraries through optional
#     flags we'll need to make Circuit accept arbitrary paths to the needed tech
#     files.
TECH = "NanGate15nm"


def parse_generate(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Invalid generate_dataset value: {value}. Must be int or float."
            )


def main():
    parser = argparse.ArgumentParser(
        description="AxLS CLI. Provides a simplified interface to the package's functionality."
    )

    subparsers = parser.add_subparsers(
        title="subcommands", dest="subcommand", required=True
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run Approximate Logic Synthesis on a circuit using one of the provided methods.",
    )

    run_arguments(run_parser)

    generate_parser = subparsers.add_parser(
        "generate", help="Generate a dataset that can be used with the 'run' command."
    )

    generate_arguments(generate_parser)

    args = parser.parse_args()

    if args.subcommand == "run":
        metrics: List[str] = args.metrics
        if len(metrics) == 0:
            metrics = [ Metric.MEAN_RELATIVE_ERROR_DISTANCE ]

        try:
            circuit = Circuit(args.circuit, TECH)
            config = ApproxSynthesisConfig(
                method=args.method,
                circuit=circuit,
                metrics=args.metrics,
                dataset=args.dataset,
                resynthesis=args.resynthesis,
                error=args.error,
                max_iters=args.max_iters,
                max_depth=args.max_depth,
                one_tree_per_output=args.one_tree_per_output,
                show_progress=args.show_progress,
            )
        except ValueError as e:
            parser.error(str(e))

        print("Configuration loaded successfully")
        print(config)

    elif args.subcommand == "generate":
        generate_dataset(args)


def run_arguments(run_parser):
    """
    Adds the arguments to the 'run' subcomand parser
    """

    run_parser.add_argument(
        "method",
        type=str,
        choices=[m.value for m in AlsMethod],
        help="Approximation method.",
    )
    run_parser.add_argument("circuit", help="Verilog circuit file.")
    run_parser.add_argument("dataset", help="Dataset file to run simulations with.")
    run_parser.add_argument(
        "metrics",
        nargs="*",
        choices=[m.value for m in Metric],
        # TODO: Add docs about what each metric is
        help="Metrics to calculate, defaults to mred.",
    )
    run_parser.add_argument(
        "--resynthesis", action="store_true", help="If provided will use resynthesis."
    )
    run_parser.add_argument(
        "--error",
        type=float,
        help="Maximum error threshold to stop iterations. (0 < x <= 1). The error used is Mean Relative Error Distance.",
    )
    run_parser.add_argument(
        "--max-iters",
        type=int,
        help="Maximum number of iterations for iterative methods.",
    )
    run_parser.add_argument(
        "--max-depth", type=int, help="Max depth for decision_tree method"
    )
    run_parser.add_argument(
        "--one-tree-per-output",
        action="store_true",
        help="Use one tree per output for decision_tree",
    )
    run_parser.add_argument(
        "--show-progress", action="store_true", help="Show simulation progress"
    )
    run_parser.add_argument(
        "--csv",
        type=str,
        help="""Path to a file to save the output in csv format.
        If the file doesn't exist, it will be created, if it exists it will be appended to.
        The output will be given as a single line with the following columns:
            method, circuit, flag1, flag2, ...,  metric1, metric2, ...""",
    )


def generate_arguments(generate_parser):
    """
    Adds the arguments to the 'generate' subcomand parser
    """
    generate_parser.add_argument("circuit", help="Verilog circuit file.")
    generate_parser.add_argument("dataset", help="Dataset file to generate.")
    generate_parser.add_argument(
        "size",
        type=parse_generate,
        help="""The size of the dataset.
        Accepts an int (x > 0, a set amount of samples), or a float (0 < x <= 1, a of the total amount of inputs possible).
        Note that for big circuits, like those with 32 input bits or more, generating a large fraction of the possible inputs might take a long time, due to the amount of possible inputs growing exponentially (2^n).
        """,
    )


def generate_dataset(args: argparse.Namespace):
    circuit = Circuit(args.circuit, TECH)

    size = args.size
    if isinstance(size, int):
        if not size > 0:
            raise argparse.ArgumentTypeError(
                f"Dataset size must be greater than 0: {size}"
            )

    if isinstance(size, float):
        if not (0 < size <= 1.0):
            raise argparse.ArgumentTypeError(
                f"Dataset size must be greater than 0: {size}"
            )

        max_inputs = 2 ** (len(circuit.inputs))
        size = round(max_inputs * size)

    circuit.generate_dataset(args.dataset, size)


if __name__ == "__main__":
    main()
