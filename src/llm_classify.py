import json
from typing import Any, Dict, List, Literal, Optional, Set, get_args

from openai import OpenAI

from providers import PROVIDERS_TYPE, parse_provider
from prompt import get_prompt
from src.util import print_err


CONFIDENCE_LEVELS_TYPE = Literal["NONE", "LOW", "MEDIUM", "HIGH"]
CONFIDENCE_LEVELS: Set[CONFIDENCE_LEVELS_TYPE] = set(get_args(CONFIDENCE_LEVELS_TYPE))


model="GLM-4.5-Air-AWQ"

client = OpenAI(
    base_url=
    # api_key="sk-123"
)

def parse_confidence(confidence: str | None) -> CONFIDENCE_LEVELS_TYPE | None:
    if confidence in CONFIDENCE_LEVELS:
        return confidence
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
    messages = get_prompt(line)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    
    response_content = response.choices[0].message.content

    return ClassificationResponse(line, response_content)


def classify_lines(
    lines: List[str],
    model: str,
) -> List[ClassificationResponse]:
    results: List[ClassificationResponse] = []
    for line in lines:
        results.append(classify_single_line(line, model))
    return results
