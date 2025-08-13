import json
from typing import Any, Dict, List, Literal, Optional, Set, get_args

import ollama


PROVIDERS_TYPE = Literal[
    "openai",
    "anthropic",
    "google",
    "gemini",
    "grok",
    "xai",
    "groq",
    "deepseek",
    "mistral",
    "cohere",
    "black_forest_labs",
    "together",
    "perplexity",
    "openrouter",
    "replicate",
    "fireworks",
    "deepinfra",
    "azure",
    "azure_openai",
    "aws",
    "bedrock",
    "aws_bedrock",
    "huggingface",
    "stability_ai",
    "nvidia",
    "unknown",
]
PROVIDERS: Set[PROVIDERS_TYPE] = set(get_args(PROVIDERS_TYPE))

CONFIDENCE_LEVELS_TYPE = Literal["NONE", "LOW", "MEDIUM", "HIGH"]
CONFIDENCE_LEVELS: Set[CONFIDENCE_LEVELS_TYPE] = set(get_args(CONFIDENCE_LEVELS_TYPE))


def parse_confidence(confidence: str | None) -> CONFIDENCE_LEVELS_TYPE | None:
    if confidence in CONFIDENCE_LEVELS:
        return confidence
    return None


def parse_provider(providers: str | None) -> PROVIDERS_TYPE | None:
    if providers in PROVIDERS:
        return providers
    return None


def shallow_extract_json(text: str) -> Optional[str]:
    """
    Note: Returned JSON may not be valid.
    """
    start_idx = None
    for i, ch in enumerate(text):
        if ch == "{":
            if start_idx is None:
                start_idx = i
        elif ch == "}":
            if start_idx is not None:
                return text[start_idx : i + 1]
    return None


def build_prompt(line: str) -> List[Dict[str, str]]:
    providers_string = ", ".join(PROVIDERS)
    system = (
        "You are an AI model designed to determine if a line contains an API key.\n"
        "Output ONLY a JSON object with the following properties:\n"
        "confidence: How confident you are that the line contains an API key. "
        "Permitted values: NONE, LOW, MEDIUM, HIGH"
        "provider: API key provider. "
        f"Permitted values: {providers_string}"
    )
    user = f"Classify the following line for presence of an API key.\n\n{line}\n"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


class ClassificationResponse:
    confidence: str | None = None
    provider: str | None = None
    line: str

    def __init__(self, line: str, response_content: str | None):
        self.line = line
        if response_content == None:
            return
        response_json = shallow_extract_json(response_content)
        if response_json == None:
            return
        try:
            json_object: Dict[str, Any] = json.loads(response_json)
            self.confidence = parse_confidence(json_object.get("confidence", None))
            self.provider = parse_provider(json_object.get("provider", None))
        finally:
            pass


def classify_single_line(
    line: str,
    model: str,
) -> ClassificationResponse:
    messages = build_prompt(line)

    response = ollama.chat(
        model=model,
        messages=messages,
        options={"temperature": 0},
    )

    response_content = response.message.content

    return ClassificationResponse(line, response_content)


def classify_lines(
    lines: List[str],
    model: str,
) -> List[ClassificationResponse]:
    results: List[ClassificationResponse] = []
    for line in lines:
        results.append(classify_single_line(line, model))
    return results
