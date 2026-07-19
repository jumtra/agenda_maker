import argparse

from agenda_maker.common import DEFAULT_CONFIG_PATH
from agenda_maker.main import make_agenda


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-config", "--config_path", default=DEFAULT_CONFIG_PATH, type=str)
    parser.add_argument("-input", "--input_path", default="sample_data/sample.mp4", type=str)
    parser.add_argument("-output", "--output_name", default="result", type=str)
    args = parser.parse_args()
    make_agenda(path_input=args.input_path, config_path=args.config_path, output_name=args.output_name)


if __name__ == "__main__":
    main()
