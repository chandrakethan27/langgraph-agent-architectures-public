def extract_text_content(content) -> str:
    """Extracts plain string text from LLM response content.
    Handles both standard str returns and Anthropic Claude 5 / Opus 5 list of content blocks
    (e.g., thinking blocks, signature blocks, text blocks).
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text" and "text" in item:
                    text_parts.append(item["text"])
                elif "text" in item and item.get("type") != "thinking":
                    text_parts.append(item["text"])
            elif isinstance(item, str):
                text_parts.append(item)
            elif hasattr(item, "text") and getattr(item, "type", None) != "thinking":
                text_parts.append(getattr(item, "text"))
        return "".join(text_parts).strip()
    return str(content)
