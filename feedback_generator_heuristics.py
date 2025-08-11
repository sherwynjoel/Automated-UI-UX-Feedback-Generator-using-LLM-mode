# feedback_generator_heuristics.py

NIELSEN_HEURISTICS = [
    "Visibility of system status",
    "Match between system and the real world",
    "User control and freedom",
    "Consistency and standards",
    "Error prevention",
    "Recognition rather than recall",
    "Flexibility and efficiency of use",
    "Aesthetic and minimalist design",
    "Help users recognize, diagnose, and recover from errors",
    "Help and documentation"
]

def heuristics_prompt_block():
    # returns a short instruction block asking the model to use the heuristics
    lines = ["You are an expert UX designer. Analyze the screenshot and produce a JSON object keyed by Nielsen's 10 heuristics. For each heuristic, return:",
             "1) verdict: Good / Needs improvement / Critical",
             "2) why: 1-2 sentences",
             "3) fix: list of 1-3 concrete fixes (short).",
             "",
             "Only include the 10 heuristics as keys. Respond only with JSON and nothing else."]
    return "\n".join(lines)
