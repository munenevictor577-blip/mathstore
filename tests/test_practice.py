import random

import sympy as sp

from mathstore.study.practice import (
    CANONICAL_TOPICS,
    PracticeQuestion,
    PracticeSession,
    check_answer,
    format_question_card,
    generate_question,
)


class TestPracticeQuestionGeneration:
    """Tests for question generators across topics and difficulties."""

    def test_canonical_topics_generation(self):
        for topic in CANONICAL_TOPICS:
            q = generate_question(topic=topic, difficulty="medium", seed=42)
            assert q.topic == topic
            assert q.prompt
            assert q.hint
            assert q.expected_answer
            assert len(q.steps) >= 1

    def test_difficulties_derivatives(self):
        for diff in ["easy", "medium", "hard"]:
            q = generate_question(topic="derivatives", difficulty=diff, seed=123)
            assert q.difficulty == diff
            assert q.question_type == "derivative"

    def test_difficulties_integrals(self):
        for diff in ["easy", "medium", "hard"]:
            q = generate_question(topic="integrals", difficulty=diff, seed=123)
            assert q.difficulty == diff
            assert q.question_type == "integral"

    def test_difficulties_algebra(self):
        for diff in ["easy", "medium", "hard"]:
            q = generate_question(topic="algebra", difficulty=diff, seed=123)
            assert q.difficulty == diff
            assert q.question_type == "roots"

    def test_difficulties_matrix(self):
        for diff in ["easy", "medium", "hard"]:
            q = generate_question(topic="matrix", difficulty=diff, seed=123)
            assert q.difficulty == diff
            assert q.question_type == "number"

    def test_difficulties_stats(self):
        for diff in ["easy", "medium", "hard"]:
            q = generate_question(topic="stats", difficulty=diff, seed=123)
            assert q.difficulty == diff
            assert q.question_type == "number"

    def test_topic_aliases(self):
        aliases = {
            "calc": "derivatives",
            "diff": "derivatives",
            "int": "integrals",
            "integrate": "integrals",
            "alg": "algebra",
            "linalg": "matrix",
            "statistics": "stats",
        }
        for alias, canonical in aliases.items():
            q = generate_question(topic=alias, seed=10)
            assert q.topic == canonical

    def test_all_topic_and_difficulty(self):
        rng = random.Random(99)
        q = generate_question(topic="all", difficulty="all", rng=rng)
        assert q.topic in CANONICAL_TOPICS
        assert q.difficulty in ["easy", "medium", "hard"]


class TestCheckAnswer:
    """Tests for symbolic equivalence and answer checking."""

    def test_check_answer_empty(self):
        q = generate_question("derivatives", seed=1)
        ok, msg = check_answer("", q)
        assert not ok
        assert "Empty" in msg

    def test_check_answer_command_words(self):
        q = generate_question("derivatives", seed=1)
        for cmd in ["hint", "skip", "quit"]:
            ok, msg = check_answer(cmd, q)
            assert not ok
            assert cmd in msg

    def test_check_answer_derivative_exact_and_equivalent(self):
        x = sp.Symbol("x")
        q = PracticeQuestion(
            topic="derivatives",
            difficulty="easy",
            prompt="Find derivative of x**2",
            expected_answer="2*x",
            hint="power rule",
            steps=["Power rule"],
            question_type="derivative",
            correct_value=2 * x,
            variable="x",
        )
        # Exact
        ok, _ = check_answer("2*x", q)
        assert ok
        # Permuted product
        ok, _ = check_answer("x*2", q)
        assert ok
        # Caret syntax
        q_pow = PracticeQuestion(
            topic="derivatives",
            difficulty="easy",
            prompt="Find derivative of x**3",
            expected_answer="3*x**2",
            hint="power rule",
            steps=["Power rule"],
            question_type="derivative",
            correct_value=3 * x**2,
            variable="x",
        )
        ok, _ = check_answer("3*x^2", q_pow)
        assert ok
        # With assignment
        ok, _ = check_answer("f'(x) = 3*x**2", q_pow)
        assert ok
        # Wrong
        ok, _ = check_answer("4*x", q)
        assert not ok
        # Syntax error
        ok, msg = check_answer("x +* 2", q)
        assert not ok
        assert "Syntax" in msg

    def test_check_answer_integral_indefinite(self):
        x = sp.Symbol("x")
        q = PracticeQuestion(
            topic="integrals",
            difficulty="easy",
            prompt="Evaluate ∫ x dx",
            expected_answer="x**2/2 + C",
            hint="power rule",
            steps=["Power rule"],
            question_type="integral",
            correct_value=x**2 / 2,
            variable="x",
            is_definite=False,
        )
        # With C
        ok, _ = check_answer("x**2 / 2 + C", q)
        assert ok
        # With lowercase c
        ok, _ = check_answer("x**2 / 2 + c", q)
        assert ok
        # Without constant
        ok, _ = check_answer("x**2 / 2", q)
        assert ok
        # Caret syntax
        ok, _ = check_answer("x^2 / 2", q)
        assert ok
        # With arbitrary constant 10
        ok, _ = check_answer("x**2 / 2 + 10", q)
        assert ok
        # Wrong
        ok, _ = check_answer("x**3", q)
        assert not ok

    def test_check_answer_integral_definite(self):
        q = PracticeQuestion(
            topic="integrals",
            difficulty="easy",
            prompt="Evaluate ∫[0 to 2] x dx",
            expected_answer="2",
            hint="FTC",
            steps=["FTC"],
            question_type="integral",
            correct_value=sp.Integer(2),
            variable="x",
            is_definite=True,
        )
        ok, _ = check_answer("2", q)
        assert ok
        ok, _ = check_answer("2.0", q)
        assert ok
        ok, _ = check_answer("4/2", q)
        assert ok
        ok, _ = check_answer("3", q)
        assert not ok

    def test_check_answer_roots(self):
        q = PracticeQuestion(
            topic="algebra",
            difficulty="medium",
            prompt="Solve x**2 - 5*x + 6 = 0",
            expected_answer="2, 3",
            hint="factor",
            steps=["Quadratic"],
            question_type="roots",
            correct_value=[sp.Integer(2), sp.Integer(3)],
            variable="x",
        )
        # Order 1
        ok, _ = check_answer("2, 3", q)
        assert ok
        # Order 2
        ok, _ = check_answer("3, 2", q)
        assert ok
        # With variables
        ok, _ = check_answer("x = 2, x = 3", q)
        assert ok
        # With brackets
        ok, _ = check_answer("[2, 3]", q)
        assert ok
        # Incomplete (only 1 root)
        ok, _ = check_answer("2", q)
        assert not ok
        # Empty roots string
        ok, _ = check_answer("[]", q)
        assert not ok

    def test_check_answer_number(self):
        q = PracticeQuestion(
            topic="matrix",
            difficulty="medium",
            prompt="Find det",
            expected_answer="14",
            hint="formula",
            steps=["Formula"],
            question_type="number",
            correct_value=14.0,
            tolerance=1e-2,
        )
        ok, _ = check_answer("14", q)
        assert ok
        ok, _ = check_answer("14.005", q)
        assert ok
        ok, _ = check_answer("15", q)
        assert not ok
        ok, _ = check_answer("invalid_num", q)
        assert not ok


class TestPracticeFormattingAndSession:
    """Tests for card formatting and interactive quiz session."""

    def test_format_question_card(self):
        q = generate_question("derivatives", seed=1)
        card = format_question_card(q, index=1)
        assert "Question #1:" in card
        assert "Hint:" in card
        assert "Expected Answer:" in card
        assert "Step-by-step solution:" in card

    def test_practice_session_all_correct(self):
        # Mock inputs: answer matching seed 42 ("2*cos(2*x)")
        answers = iter(["2*cos(2*x)"])
        outputs = []

        session = PracticeSession(
            topic="derivatives",
            count=1,
            seed=42,
            input_func=lambda _: next(answers),
            print_func=outputs.append,
        )
        summary = session.run()
        assert summary["total"] == 1
        assert summary["completed"] == 1
        assert summary["correct"] == 1
        assert summary["percentage"] == 100.0

    def test_practice_session_retry_and_skip(self):
        # 1st question: wrong, then correct
        # 2nd question: hint, then skip
        inputs = iter(["wrong_answer", "skip", "hint", "skip"])
        outputs = []

        session = PracticeSession(
            topic="algebra",
            count=2,
            seed=42,
            input_func=lambda _: next(inputs),
            print_func=outputs.append,
        )
        summary = session.run()
        assert summary["total"] == 2
        assert summary["completed"] == 2
        assert summary["skipped"] >= 1

    def test_practice_session_quit(self):
        inputs = iter(["quit"])
        outputs = []

        session = PracticeSession(
            topic="derivatives",
            count=3,
            seed=42,
            input_func=lambda _: next(inputs),
            print_func=outputs.append,
        )
        summary = session.run()
        assert summary["total"] == 3
        assert summary["completed"] == 0
        assert any("early" in str(line).lower() for line in outputs)

    def test_practice_session_keyboard_interrupt(self):
        def mock_input(_):
            raise KeyboardInterrupt

        outputs = []
        session = PracticeSession(
            topic="derivatives",
            count=2,
            input_func=mock_input,
            print_func=outputs.append,
        )
        summary = session.run()
        assert summary["completed"] == 0
        assert any("ended" in str(line).lower() for line in outputs)
