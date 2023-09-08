import os
import zipfile

__all__ = ["zip_directory"]


def zip_directory(directory_path, output_zip_file):
    """
    指定したディレクトリをZIPファイルに圧縮する関数

    Args:
        directory_path (str): 圧縮したいディレクトリのパス
        output_zip_file (str): 生成するZIPファイルの名前

    Returns:
        None
    """
    try:
        with zipfile.ZipFile(output_zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory_path)
                    zipf.write(file_path, rel_path)
        print(f'ディレクトリ "{directory_path}" を "{output_zip_file}" に圧縮しました。')
    except Exception as e:
        print(f"エラー: {e}")
