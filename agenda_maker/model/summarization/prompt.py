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
            """あなたは文章を**文語形式**で500字以内に要約するAIです。\n\n文章：""",
            "\n\n要約:",
        )
    elif task == "punctuation":
        return (
            """あなたは**文章の誤字脱字を修正し句読点を追加し、文脈が正しい文章を生成するAIです。出力には結果以外絶対に出力しないでください。\n\n文章:""",
            "\n\n文章:",
        )
    # ELYZAのデフォルトプロンプト
    return ("""あなたは誠実で優秀な日本人のアシスタントです。""", "")
