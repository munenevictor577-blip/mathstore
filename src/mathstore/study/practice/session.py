import random
from typing import Any, Callable

from mathstore.study.practice.evaluators import check_answer
from mathstore.study.practice.generators import generate_question
from mathstore.study.practice.models import PracticeQuestion

__all__ = ["PracticeSession", "format_question_card"]


class PracticeSession:
    """Interactive CLI practice quizzer with score tracking, hints, and derivations."""

    def __init__(
        self,
        topic: str = "all",
        count: int = 5,
        difficulty: str = "medium",
        seed: int | None = None,
        input_func: Callable[[str], str] | None = None,
        print_func: Callable[..., None] | None = None,
    ):
        self.topic = topic
        self.count = max(1, count)
        self.difficulty = difficulty
        self.rng = random.Random(seed)
        self.input_func = input_func if input_func is not None else input
        self.print_func = print_func if print_func is not None else print

    def run(self) -> dict[str, Any]:
        """Runs the interactive practice session."""
        self.print_func("=" * 60)
        self.print_func("  MathStore University Practice & Revision Quizzer")
        self.print_func(
            f"  Topic: {self.topic.capitalize()} | Difficulty: {self.difficulty.capitalize()} | Questions: {self.count}"
        )
        self.print_func(
            "  Commands: 'hint' for a hint, 'skip' to reveal solution, 'quit' to exit."
        )
        self.print_func("=" * 60)

        score = 0
        skipped = 0
        completed = 0
        seen_prompts: set[str] = set()
        used_subtypes: set[str] = set()

        for i in range(1, self.count + 1):
            q = generate_question(
                topic=self.topic,
                difficulty=self.difficulty,
                rng=self.rng,
                exclude_subtypes=used_subtypes,
            )
            # Avoid repeating the same question during a session
            retry_count = 0
            while q.prompt in seen_prompts and retry_count < 30:
                q = generate_question(
                    topic=self.topic,
                    difficulty=self.difficulty,
                    rng=self.rng,
                    exclude_subtypes=used_subtypes,
                )
                retry_count += 1
            seen_prompts.add(q.prompt)
            if q.subtype:
                used_subtypes.add(q.subtype)

            self.print_func(
                f"\n[Question {i}/{self.count}] ({q.topic.capitalize()} - {q.difficulty})"
            )
            self.print_func(f"  {q.prompt}")

            attempts = 0
            while True:
                try:
                    user_resp = self.input_func("  Your answer > ").strip()
                except (EOFError, KeyboardInterrupt):
                    self.print_func("\nSession ended by user.")
                    return {
                        "total": self.count,
                        "completed": completed,
                        "correct": score,
                        "skipped": skipped,
                        "percentage": (score / max(1, completed)) * 100
                        if completed
                        else 0.0,
                    }

                if user_resp.lower() == "quit":
                    self.print_func("\nExiting practice session early...")
                    self._show_summary(score, completed, skipped)
                    return {
                        "total": self.count,
                        "completed": completed,
                        "correct": score,
                        "skipped": skipped,
                        "percentage": (score / max(1, completed)) * 100
                        if completed
                        else 0.0,
                    }

                if user_resp.lower() == "hint":
                    self.print_func(f"  💡 Hint: {q.hint}")
                    continue

                if user_resp.lower() == "skip":
                    self.print_func(
                        f"  ⏭ Skipped. Expected answer: {q.expected_answer}"
                    )
                    self.print_func("  Step-by-step solution:")
                    for idx, s in enumerate(q.steps, 1):
                        self.print_func(f"    {idx}. {s}")
                    skipped += 1
                    completed += 1
                    break

                is_correct, feedback = check_answer(user_resp, q)
                if is_correct:
                    self.print_func(f"  {feedback}")
                    score += 1
                    completed += 1
                    break

                attempts += 1
                self.print_func(f"  ✗ {feedback}")
                if attempts >= 2:
                    self.print_func(f"  The correct answer was: {q.expected_answer}")
                    self.print_func("  Step-by-step solution:")
                    for idx, s in enumerate(q.steps, 1):
                        self.print_func(f"    {idx}. {s}")
                    completed += 1
                    break

        self._show_summary(score, completed, skipped)
        pct = (score / max(1, completed)) * 100 if completed else 0.0
        return {
            "total": self.count,
            "completed": completed,
            "correct": score,
            "skipped": skipped,
            "percentage": pct,
        }

    def _show_summary(self, score: int, completed: int, skipped: int) -> None:
        self.print_func("\n" + "=" * 60)
        self.print_func("  Practice Quiz Completed!")
        pct = (score / max(1, completed)) * 100 if completed else 0.0
        self.print_func(f"  Questions Attempted: {completed}/{self.count}")
        self.print_func(f"  Correct Answers:     {score}")
        self.print_func(f"  Skipped:             {skipped}")
        self.print_func(f"  Score:               {pct:.1f}%")

        if pct >= 80.0:
            self.print_func("  🌟 Outstanding! You have mastered these concepts.")
        elif pct >= 60.0:
            self.print_func(
                "  👍 Good effort! Review the tricky derivations and try again."
            )
        else:
            self.print_func(
                "  📚 Keep revising! Use 'mathstore ref' to consult cheat sheets."
            )
        self.print_func("=" * 60)

def format_question_card(q: PracticeQuestion, index: int | None = None) -> str:
    """Formats a single practice question with hints, answers, and steps for non-interactive output."""
    prefix = f"Question #{index}: " if index is not None else ""
    lines = [
        f"[{q.topic.upper()}] (Difficulty: {q.difficulty})",
        f"{prefix}{q.prompt}",
        f"Hint: {q.hint}",
        f"Expected Answer: {q.expected_answer}",
        "Step-by-step solution:",
    ]
    for idx, s in enumerate(q.steps, 1):
        lines.append(f"  {idx}. {s}")
    return "\n".join(lines)        