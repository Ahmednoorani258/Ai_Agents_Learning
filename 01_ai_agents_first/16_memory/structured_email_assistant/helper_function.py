from typing import Dict

def create_prompt(template: str, variables: Dict[str, any]) -> str:
    """Creates a prompt using an f-string and a dictionary of variables."""
    try:
        return template.format(**variables)
    except KeyError as e:
        return f"Error: Missing variable '{e.args[0]}' in the provided dictionary."
     