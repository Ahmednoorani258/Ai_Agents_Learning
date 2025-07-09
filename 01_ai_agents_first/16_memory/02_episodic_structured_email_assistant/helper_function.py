
from typing import Dict
template = """Email Subject: {subject}
Email From: {from_email}
Email To: {to_email}
Email Content:
```
{content}
```
> Triage Result: {result}
"""

def format_few_shot_examples(examples):
    print(examples)
    strs = ["\nHere are some previous examples:\n"]
    for eg in examples:
        email_data = eg.value.get("email", {})
        subject = email_data.get("subject", "No Subject")
        to_email = email_data.get("to", "No Recipient")
        from_email = email_data.get("author") or email_data.get("from", "No Sender")
        # Use 'email_thread' if available; otherwise fall back to 'body'
        content = email_data.get("email_thread") or email_data.get("body", "")
        # Truncate the content to a maximum of 400 characters
        content = content[:400]
        result = eg.value.get("label", "No Label")

        strs.append(
            template.format(
                subject=subject,
                to_email=to_email,
                from_email=from_email,
                content=content,
                result=result,
            )
        )
    return "\n\n------------\n\n".join(strs)
    

def create_prompt(template: str, variables: Dict[str, any]) -> str:
    """Creates a prompt using an f-string and a dictionary of variables."""
    try:
        return template.format(**variables)
    except KeyError as e:
        return f"Error: Missing variable '{e.args[0]}' in the provided dictionary."
