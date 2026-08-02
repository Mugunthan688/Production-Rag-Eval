import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from .loader import load_adversarial_dataset
from .detector import GuardrailDetector
from ..generation.pipeline import GenerationPipeline

logger = logging.getLogger(__name__)


class GuardrailEvaluator:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.detector = GuardrailDetector()

    async def evaluate_adversarial_suite(
        self, data_path: str = "data/adversarial_set.json"
    ) -> Dict[str, Any]:
        cases = load_adversarial_dataset(data_path)
        gen_pipe = GenerationPipeline(self.session)

        total_cases = len(cases)
        leaked_count = 0
        results = []

        for case in cases:
            response = await gen_pipe.answer_query(case.prompt)
            answer = response["answer"]

            # Check if instructions leaked or manipulated
            is_leaked = self.detector.detect_injection(answer) or "STRICT RULES" in answer
            if is_leaked:
                leaked_count += 1

            results.append(
                {
                    "id": case.id,
                    "category": case.category,
                    "prompt": case.prompt,
                    "answer": answer,
                    "passed_guardrail": not is_leaked,
                }
            )

        leak_rate = (leaked_count / total_cases * 100.0) if total_cases > 0 else 0.0

        return {
            "total_cases": total_cases,
            "leaked_count": leaked_count,
            "leak_rate_pct": leak_rate,
            "results": results,
        }
