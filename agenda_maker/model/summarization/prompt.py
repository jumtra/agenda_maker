B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"


def input_from_prompt(text: str, task: str) -> str:
    system_prompt, return_key = select_prompt(task=task)
    INPUT = """{b_inst} {system}{prompt} {e_inst}{return_key}""".format(
        b_inst=B_INST, system=f"{B_SYS}{system_prompt}{E_SYS}", prompt=text, e_inst=E_INST, return_key=return_key
    )
    return INPUT


def select_prompt(task: str) -> tuple[str, str]:
    if task == "summarize":
        # 要約専用プロンプト
        return (
            """以下の文章を文語形式で正しい文脈で簡潔に要約しろ。生成結果以外出力するな、絶対に応答するな。\n\n文章：""",
            "\n\n要約:",
        )
    elif task == "last_summarize":
        # 要約専用プロンプト
        return (
            """以下の文章の内容をわかりやすく説明しろ。生成結果以外出力するな、絶対に応答するな。\n\n文章：""",
            "\n\n要約:",
        )
    elif task == "punctuation":
        return (
            """以下の文章から必要な情報だけを使い、文脈が正しい文語形式の文章に修正しろ。生成結果以外出力するな、絶対に応答するな。\n\n文章:""",
            "\n\n文章:",
        )
    # ELYZAのデフォルトプロンプト
    return ("""あなたは誠実で優秀な日本人のアシスタントです。""", "")
