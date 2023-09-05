import argparse

from agenda_maker.main import make_agenda


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-config", "--config_path", default="agenda_maker/config/config.yaml", type=str)
    parser.add_argument("-input", "--input_path", default="data/sample.mp3", type=str)
    parser.add_argument("-output", "--output_name", default="./result", type=str)
    args = parser.parse_args()
    config_path = args.config_path
    path_input = args.input_path
    output_name = args.output_name
    make_agenda(path_input=path_input, config_path=config_path, output_name=output_name)


if __name__ == "__main__":
    main()
