import argparse
from pathlib import Path

from agenda_maker.common.config_manager import ConfigManager
from agenda_maker.model.transcription import WhisperX


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-config", "--config_path", default="agenda_maker/config/config.yaml", type=str)
    parser.add_argument("-input", "--input_path", default="data/sample.mp3", type=str)
    parser.add_argument("-output", "--output_name", default=None, type=str)

    args = parser.parse_args()
    config_path = args.config_path
    config_dir = str("/".join(Path(config_path).parts[:-1]))
    config_yaml_path = str(Path(config_path).parts[-1])
    config_manager = ConfigManager.from_yaml(
        config_yaml_path=config_yaml_path,
        config_dir=config_dir,
    )
    output = args.output_name
    config_manager.config.output.output_dir = str(Path(config_manager.config.output.output_dir_base) / output)
    input_path = args.input_path

    Path(config_manager.config.output.output_dir).mkdir(exist_ok=True, parents=True)
    result = WhisperX(config_manager=config_manager).get_result(input_path=input_path)
    result.df_result.to_csv(config_manager.config.output.path_whisperx_file, index=False)
    result.df_word_seg.to_csv(config_manager.config.output.path_seg_word_file, index=False)


if __name__ == "__main__":
    main()
