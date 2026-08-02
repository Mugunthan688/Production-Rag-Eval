import json
import logging
from typing import List
from pathlib import Path

from src.guardrails.schemas import AdversarialTestCase

logger = logging.getLogger(__name__)


def load_adversarial_dataset(file_path: str = "data/adversarial_set.json") -> List[AdversarialTestCase]:
    path = Path(file_path)
    if not path.exists():
        logger.warning(f"Adversarial dataset path {file_path} does not exist. Returning empty list.")
        return []

    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    cases = [AdversarialTestCase(**item) for item in raw_data]
    logger.info(f"Loaded {len(cases)} adversarial test cases from {file_path}")
    return cases
