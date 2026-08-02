import json
import logging
from typing import List
from pathlib import Path

from src.evaluation.schemas import EvalQuestion

logger = logging.getLogger(__name__)


def load_eval_dataset(file_path: str = "data/eval_set.json") -> List[EvalQuestion]:
    path = Path(file_path)
    if not path.exists():
        logger.warning(f"Eval dataset path {file_path} does not exist. Returning empty list.")
        return []

    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    questions = [EvalQuestion(**item) for item in raw_data]
    logger.info(f"Loaded {len(questions)} evaluation questions from {file_path}")
    return questions
