import re
from typing import List, Set, TypedDict

import requests

from gists import GistInfo, get_gist_info
from preprocess import normalize_all_contents
from classify import (
    CONFIDENCE_LEVELS_TYPE,
    ClassificationResponse,
    classify_lines,
)
from verify import verify, VALIDITY
from save import save_record


def _get_value_from_env(line: str) -> str | None:
    # Gets everything after the first "="
    match = re.match(r"^[^=]+=(.+)$", line)
    if match == None:
        return None
    value = match.group(1)
    if value == None:
        return None
    value = value.strip()
    # Strip surrounding quotes if any
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        value = value[1:-1]
    if value == "":
        return None
    return value


class ProcessGistResult(TypedDict):
    path: str
    owner: str
    gist_id: str
    confidence: CONFIDENCE_LEVELS_TYPE
    validity: VALIDITY
    line: str


def process_gist(
    gist_id: str,
    file_type: str,
    model: str,
    output_dir: str,
) -> List[ProcessGistResult]:
    """
    Process a single gist: fetch contents, filter, classify, verify, and save.

    Note: Save a record when verification result is "UNKNOWN" or "VALID".
    """
    session = requests.Session()
    try:
        gist_info: GistInfo = get_gist_info(session, gist_id, file_type)

        lines: List[str] = normalize_all_contents(gist_info.file_contents, file_type)

        classifications: List[ClassificationResponse] = classify_lines(lines, model)

        # Track already-verified keys to avoid duplicate checks per gist
        checked_values: Set[str] = set()

        result: List[ProcessGistResult] = []

        for classification_response in classifications:
            confidence, provider, line = (
                classification_response.confidence,
                classification_response.provider,
                classification_response.line,
            )

            if confidence == None or provider == None:
                continue
            if confidence == "NONE":
                continue

            # TODO: Support more file types
            value = _get_value_from_env(line)

            if value == None:
                continue

            if value in checked_values:
                continue

            checked_values.add(value)

            validity: VALIDITY = verify(provider, value)

            if (
                validity == "VALID"
                or (validity == "UNKNOWN" and confidence in ["MEDIUM", "HIGH"])
                or confidence == "HIGH"
            ):
                path = save_record(
                    output_dir=output_dir,
                    gist_id=gist_id,
                    owner=gist_info.owner,
                    provider=provider,
                    confidence=confidence,
                    validity=validity,
                    line=line,
                )
                result.append(
                    {
                        "path": path,
                        "owner": gist_info.owner,
                        "gist_id": gist_id,
                        "confidence": confidence,
                        "validity": validity,
                        "line": line,
                    }
                )

        return result
    finally:
        session.close()
