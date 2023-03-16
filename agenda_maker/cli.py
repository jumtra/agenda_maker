
import argparse

from agenda_maker.main import make_agenda


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-config", "--config_path", default="agenda_maker/config/config.yaml", type=str
    )
    parser.add_argument("-in", "--path_input", default=None, type=str)
    parser.add_argument("-out", "--path_output", default="./result", type=str)
    args = parser.parse_args()
    config_path = args.config_path
    path_input = args.path_input
    path_output = args.path_output
    make_agenda(
        path_input=path_input,
        path_output=path_output,
        config_path=config_path,
    )


if __name__ == "__main__":
    main()
