B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = """あなたは与えられた文章を必ず文語形式で要約するAIです。
要約は「要約：」ではじめてください。
与えられた文章の内容と要約の内容は、必ず同じ内容にしてください。
要約結果は、必ず300字以内にしてください。

文章："""


def input_from_prompt(text: str) -> str:
    INPUT = """{b_inst} {system}{prompt} {e_inst} """.format(
        b_inst=B_INST,
        system=f"{B_SYS}{DEFAULT_SYSTEM_PROMPT}{E_SYS}",
        prompt=text,
        e_inst=E_INST,
    )
    return INPUT
