import argparse
import os
from typing import List
from configuration import ApproxSynthesisConfig, AlsMethod


def parse_generate(value):
    if value == "exhaustive":
        return value

    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Invalid generate_dataset value: {value}. Must be int, float or 'exhaustive'."
            )


def parse_subset(value):
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
        description="AxLS CLI. Can execute the different Approximate Logic Synthesis methods available with some configuration options."
    )
    parser.add_argument(
        "--method",
        required=True,
        type=str,
        choices=[m.value for m in AlsMethod],
        help="Approximation method.",
    )
    parser.add_argument(
        "--circuit", required=True, nargs="+", help="Verilog circuit file(s)."
    )
    parser.add_argument("--dataset", required=True, nargs="+", help="Dataset file(s).")
    parser.add_argument(
        "--generate",
        nargs="+",
        type=parse_generate,
        help="If provided, the dataset file(s) will be generated instead of looking for existing ones. This will overwrite any existing files. Accepts int (the amount of samples), float (between 0-1, a percentage of all the possible inputs) or 'exhaustive' (generate all possible inputs for a circuit, only usable for circuits with less than 32 input bits).",
    )
    parser.add_argument(
        "--subset",
        nargs="+",
        type=parse_subset,
        help="If provided, will only use a subset of the existing dataset file(s). Accepts int (the amount of samples) or float (0 < x <= 1, a percentage of the available samples).",
    )
    parser.add_argument(
        "--resynthesis", action="store_true", help="If provided will use resynthesis."
    )
    parser.add_argument(
        "--error",
        type=float,
        help="Maximum error threshold to stop iterations. (0 < x <= 1).",
    )
    parser.add_argument(
        "--max-iters",
        type=int,
        help="Maximum number of iterations for iterative methods.",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Path to a file to save the run's configuration and progress.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="If provided, will resume from the existing save file.",
    )
    parser.add_argument(
        "--max-depth", nargs="+", type=int, help="Max depth for decision_tree method"
    )
    parser.add_argument(
        "--one-tree-per-output",
        action="store_true",
        help="Use one tree per output for decision_tree",
    )
    parser.add_argument(
        "--show-progress", action="store_true", help="Show simulation progress"
    )
    args = parser.parse_args()

    # number of circuits
    n = len(args.circuit)

    def check_list[T](name: str, lst: List[T]) -> T | List[T]:
        ln = len(lst)
        if ln == 1:
            return lst[0]
        elif ln == n:
            return lst
        else:
            if n == 1:
                parser.error(
                    f"--{name} only accepts 1 value when only 1 circuit is given, got {ln} values"
                )
            else:
                parser.error(f"--{name} requires 1 or {n} values, got {ln}")

    # align lists
    args.circuit = check_list("circuit", args.circuit)
    args.dataset = check_list("dataset", args.dataset)

    if args.generate:
        args.generate = check_list("generate", args.generate)
    if args.subset:
        args.subset = check_list("subset", args.subset)

    if args.max_depth:
        args.max_depth = check_list("max-depth", args.max_depth)

    # exclusivity checks
    if args.generate and args.subset:
        parser.error("Cannot specify both --generate and --subset")

    if args.resume:
        if not args.save:
            parser.error("--save is required when --resume is set")
        if not os.path.isfile(args.save):
            parser.error(f"Save file does not exist: {args.save}")

    # instantiate config
    try:
        config = ApproxSynthesisConfig(
            method=args.method,
            circuit=args.circuit,
            dataset=args.dataset,
            generate=args.generate,
            subset=args.subset,
            resynthesis=args.resynthesis,
            error=args.error,
            max_iters=args.max_iters,
            save=args.save,
            resume=args.resume,
            max_depth=args.max_depth,
            one_tree_per_output=args.one_tree_per_output,
            show_progress=args.show_progress,
        )
    except ValueError as e:
        parser.error(str(e))

    print("Configuration loaded successfully")
    print(config)


if __name__ == "__main__":
    main()
