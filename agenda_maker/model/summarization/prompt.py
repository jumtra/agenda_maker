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
            """あなたは文章を**文語形式**で要約するAIです。\n文章：""",
            "\n\n 要約:",
        )
    elif task == "punctuation":
        return (
            """あなたは誠実で優秀な日本人のアシスタントです。\n次の**文章の誤字脱字を修正し句読点を追加した文脈が正しい文章**を生成してください。
        文章：""",
            "",
        )
    # ELYZAのデフォルトプロンプト
    return ("""あなたは誠実で優秀な日本人のアシスタントです。""", "")
