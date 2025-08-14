import json
from typing import Any, Dict, List, Literal, Optional, Set, get_args

import ollama

from util import print_err


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
    "github",
    "copilot"
    "other",
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
    end_index = None
    for i, ch in reversed(list(enumerate(text))):
        if ch == "}":
            if end_index is None:
                end_index = i
        elif ch == "{":
            if end_index is not None:
                return text[i : end_index + 1]
    return None


def build_prompt(line: str) -> List[Dict[str, str]]:
    providers_string = ", ".join(PROVIDERS)
    system = (
        "You are a highly specialized AI assistant tasked with analyzing a single variable from a .env file. "
        "Your primary task is to determine if the value of the variable contains a potentially valid API key. "
        "Your output must be in a strict JSON format with two keys: `confidence` and `provider`."
        "\n\n"
        "The `confidence` key indicates how confident you are that the value is a potentially valid API key. "
        "The confidence value must be a string value from the following list: "
        '"NONE", "LOW", "MEDIUM", "HIGH".'
        "\n"
        "The `provider` key indicates the provider of the API key. "
        f"The value must be a value from the following list: {providers_string}"
        "\n"
        "A potentially valid API key does not include example values or placeholder values. "
        "A potentially valid API key should be directly usable for authentiating an API request."
    )
    user = f"Analyze the following variable:\n{line}\n"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


class ClassificationResponse:
    confidence: CONFIDENCE_LEVELS_TYPE | None = None
    provider: PROVIDERS_TYPE | None = None
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
        except Exception as exception:
            print_err(f"ClassificationResponse exception: {exception}")
            print_err(f"Response Content: {response_content}")
            print_err(f"Response JSON: {response_json}")


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
