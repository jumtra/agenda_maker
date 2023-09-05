B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = """あなたは文章を**文語形式**で要約するAIです。

文章："""
# 与えられた文章と要約の内容は、必ず同じ内容にしてください。
# 要約と関係ない文章は絶対に生成しないでください。


def input_from_prompt(text: str) -> str:
    INPUT = """{b_inst} {system}{prompt} {e_inst}\n\n 要約:""".format(
        b_inst=B_INST,
        system=f"{B_SYS}{DEFAULT_SYSTEM_PROMPT}{E_SYS}",
        prompt=text,
        e_inst=E_INST,
    )
    return INPUT
