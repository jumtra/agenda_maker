import argparse

from agenda_maker.common import add_stage_arguments, load_stage_config
from agenda_maker.model.transcription import WhisperX


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_stage_arguments(parser, require_input=True, default_output_name=None)
    args = parser.parse_args()

    config_manager = load_stage_config(args.config_path, args.output_name)
    result = WhisperX(config_manager=config_manager).get_result(input_path=args.input_path)
    result.df_result.to_csv(config_manager.config.output.path_whisperx_file, index=False)
    result.df_word_seg.to_csv(config_manager.config.output.path_seg_word_file, index=False)


if __name__ == "__main__":
    main()
