

BLOCK_MODE_PROMPT = (
    "You should always follow the instructions and output a valid {{block}} object."
    "The structure of the {{block}} object you can found in the instructions, "
    "use {\"answer\": \"$your_answer\"} as the default structure "
    "if you are not sure about the structure.\n\n"
    "<instructions>\n"
    "{{instructions}}\n"
    "</instructions>"
)
