import random
from unittest.mock import patch

import sympy as sp

from mathstore.study.practice import (
    CANONICAL_TOPICS,
    TOPIC_ALIASES,
    PracticeQuestion,
    PracticeSession,
    _gen_algebra_question,
    _gen_derivative_question,
    _gen_integral_question,
    _gen_matrix_question,
    _gen_stats_question,
    check_answer,
    format_question_card,
    generate_question,
)


class TestPracticeQuestionGeneration:
    """Tests for question generators across topics and difficulties."""

    def test_question_generation_all_branches(self):
        rng = random.Random(42)

        # Derivatives: easy trig (lines 205-210)
        with patch.object(rng, "choice", side_effect=["trig", sp.sin]):
            q_der_trig = _gen_derivative_question("easy", rng)
            assert q_der_trig.topic == "derivatives"

        # Derivatives: medium chain_exp (lines 222-226)
        with patch.object(rng, "choice", side_effect=["chain_exp", 3, 2]):
            q_der_exp = _gen_derivative_question("medium", rng)
            assert "exp" in q_der_exp.prompt

        # Derivatives: hard prod_trig_exp (lines 243-249)
        with patch.object(rng, "choice", side_effect=["prod_trig_exp", 2]):
            q_der_pte = _gen_derivative_question("hard", rng)
            assert "exp" in q_der_pte.prompt

        # Derivatives: hard quotient (lines 250-254)
        with patch.object(rng, "choice", side_effect=["quotient"]):
            q_der_q = _gen_derivative_question("hard", rng)
            assert "quotient" in q_der_q.hint.lower()

        # Integrals: easy trig (lines 283-288)
        with patch.object(rng, "choice", side_effect=["trig", sp.sin]):
            q_int_trig = _gen_integral_question("easy", rng)
            assert q_int_trig.topic == "integrals"

        # Integrals: medium reciprocal (lines 344-362)
        with patch.object(rng, "choice", side_effect=["reciprocal"]):
            q_int_rec = _gen_integral_question("medium", rng)
            assert "1/x" in q_int_rec.hint or "ln" in q_int_rec.hint

        # Integrals: medium exp (lines 326-332)
        with patch.object(rng, "choice", side_effect=["exp", 2]):
            q_int_exp = _gen_integral_question("medium", rng)
            assert "exp" in q_int_exp.prompt

        # Integrals: medium definite (lines 363-370)
        with patch.object(rng, "choice", side_effect=["definite"]):
            q_int_def = _gen_integral_question("medium", rng)
            assert q_int_def.is_definite

        # Integrals: hard parts_trig (lines 390-395)
        with patch.object(rng, "choice", side_effect=["parts_trig"]):
            q_int_pt = _gen_integral_question("hard", rng)
            assert "parts" in q_int_pt.prompt.lower()

        # Integrals: hard arctan_form (lines 396-399)
        with patch.object(rng, "choice", side_effect=["arctan_form"]):
            q_int_at = _gen_integral_question("hard", rng)
            assert (
                "atan" in q_int_at.expected_answer or "arctan" in q_int_at.hint.lower()
            )

        # Algebra: medium monic quadratic (lines 465-472)
        with patch.object(rng, "choice", side_effect=["monic_quadratic"]):
            q_alg = _gen_algebra_question("medium", rng)
            assert q_alg.topic == "algebra"

        # Matrix: easy diag_det (lines 529-538)
        with patch.object(rng, "choice", side_effect=["diag_det"]):
            q_mat_diag = _gen_matrix_question("easy", rng)
            assert "diagonal" in q_mat_diag.prompt.lower()

        # Matrix: hard triangular determinant (lines 595-606)
        with patch.object(rng, "choice", side_effect=["triangular_det"]):
            q_mat_tri = _gen_matrix_question("hard", rng)
            assert "triangular" in q_mat_tri.prompt.lower()

        # Statistics: easy median (lines 641-651)
        with patch.object(rng, "choice", side_effect=["median"]):
            q_stat_med = _gen_stats_question("easy", rng)
            assert "median" in q_stat_med.prompt.lower()

        # Statistics: medium range (lines 687-696)
        with patch.object(rng, "choice", side_effect=["range"]):
            q_stat_range = _gen_stats_question("medium", rng)
            assert "range" in q_stat_range.prompt.lower()

        # Fallback in generate_question (line 760)
        with patch.dict(
            TOPIC_ALIASES, {"custom_unmapped": "unmapped_val"}, clear=False
        ):
            q_fallback = generate_question("custom_unmapped", rng=rng)
            assert q_fallback.topic == "derivatives"

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

    def test_check_answer_edge_cases(self):
        # Line 110: correct_value is a single scalar integer
        q_root_scalar = PracticeQuestion(
            topic="algebra",
            difficulty="easy",
            prompt="Solve x - 5 = 0",
            expected_answer="5",
            hint="",
            steps=[],
            question_type="roots",
            correct_value=5,
            variable="x",
        )
        ok, _ = check_answer("5", q_root_scalar)
        assert ok

        # Lines 128-129: Unparseable roots format
        ok, msg = check_answer("@@@@", q_root_scalar)
        assert not ok
        assert "Could not parse roots format" in msg

        # Lines 163-165: Numerical match within tolerance for definite integral
        q_def_int = PracticeQuestion(
            topic="integrals",
            difficulty="medium",
            prompt="Definite integral",
            expected_answer="3.14159",
            hint="",
            steps=[],
            question_type="integral",
            correct_value=sp.pi,
            is_definite=True,
            tolerance=0.05,
            variable="x",
        )
        ok_tol, _ = check_answer("3.14", q_def_int)
        assert ok_tol

        # Lines 164-165: Symbolic answer for definite integral raises TypeError in float()
        ok_sym, _ = check_answer("x", q_def_int)
        assert not ok_sym

        # Lines 174-175: Syntax error in integral expression
        ok_err, msg_err = check_answer("++**", q_def_int)
        assert not ok_err
        assert "Syntax error" in msg_err

        # Line 189: Unsupported question type
        q_unsupported = PracticeQuestion(
            topic="study",
            difficulty="easy",
            prompt="test",
            expected_answer="1",
            hint="",
            steps=[],
            question_type="unknown_question_type",
        )
        ok_unsupp, msg_unsupp = check_answer("1", q_unsupported)
        assert not ok_unsupp
        assert msg_unsupp == "Unsupported question type."

        # Lines 112-113: correct_value is None for roots question
        q_roots_none = PracticeQuestion(
            topic="algebra",
            difficulty="easy",
            prompt="Solve x^2 - 1 = 0",
            expected_answer="x = -1, x = 1",
            hint="",
            steps=[],
            question_type="roots",
            correct_value=None,
            variable="x",
        )
        ok_none, _ = check_answer("-1, 1", q_roots_none)
        assert ok_none

        # Line 153: target_raw is a string for indefinite integral
        q_int_str = PracticeQuestion(
            topic="integrals",
            difficulty="easy",
            prompt="∫ 2*x dx",
            expected_answer="x**2 + C",
            hint="",
            steps=[],
            question_type="integral",
            correct_value=None,
            variable="x",
        )
        ok_int_str, _ = check_answer("x**2 + C", q_int_str)
        assert ok_int_str

    def test_roots_matching_with_string_list(self):
        q = PracticeQuestion(
            topic="algebra",
            difficulty="medium",
            prompt="Solve x^2 - 5*x + 6 = 0",
            expected_answer="2, 3",
            hint="factor",
            question_type="roots",
            correct_value=["2", "3"],
        )
        is_correct, feedback = check_answer("3, 2", q)
        assert is_correct is True
        assert "Correct" in feedback

    def test_fallback_when_correct_value_none(self):
        # Roots fallback
        q_roots = PracticeQuestion(
            topic="algebra",
            difficulty="medium",
            prompt="Solve x^2 - 5*x + 6 = 0",
            expected_answer="2, 3",
            hint="factor",
            question_type="roots",
            correct_value=None,
        )
        assert check_answer("2, 3", q_roots)[0] is True

        # Derivative fallback
        q_diff = PracticeQuestion(
            topic="derivatives",
            difficulty="easy",
            prompt="Differentiate x**2",
            expected_answer="2*x",
            hint="power rule",
            question_type="derivative",
            correct_value=None,
        )
        assert check_answer("2*x", q_diff)[0] is True

        # Number fallback
        q_num = PracticeQuestion(
            topic="stats",
            difficulty="easy",
            prompt="Find mean",
            expected_answer="15.5",
            hint="sum/n",
            question_type="number",
            correct_value=None,
        )
        assert check_answer("15.5", q_num)[0] is True

        # Integral fallback
        q_int = PracticeQuestion(
            topic="integrals",
            difficulty="easy",
            prompt="Integrate x^2",
            expected_answer="x**3/3 + C",
            hint="power rule",
            question_type="integral",
            correct_value=None,
        )
        assert check_answer("x**3/3", q_int)[0] is True


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
        outputs = []
        gen_rng = random.Random(42)
        q = generate_question(topic="derivatives", difficulty="medium", rng=gen_rng)
        answers = iter([str(q.expected_answer)])

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

    def test_practice_session_two_failed_attempts(self):
        fail_inputs = iter(["wrong_answer_1", "wrong_answer_2"])
        session = PracticeSession(
            count=1,
            input_func=lambda _: next(fail_inputs),
            print_func=lambda *args: None,
        )
        res = session.run()
        assert res["correct"] == 0
        assert res["completed"] == 1

    def test_practice_session_score_tiers(self):
        printed = []
        session = PracticeSession(count=5, print_func=printed.append)
        session._show_summary(score=3, completed=5, skipped=2)
        assert any("Good effort" in str(line) for line in printed)

    def test_derivatives_unique_questions_with_seed(self):
        """Verify that 5 questions generated with seed 42 are unique deterministically."""
        my_rng = random.Random(42)
        questions = [generate_question(topic="derivatives", rng=my_rng) for _ in range(5)]
        prompts = [q.prompt for q in questions]
        assert len(set(prompts)) == 5

    def test_matrix_negative_entries(self):
        """Verify that matrix questions can have negative entries."""
        rng = random.Random(42)
        negative_found = False
        for diff in ["easy", "medium", "hard"]:
            for _ in range(20):
                q = generate_question(topic="matrix", difficulty=diff, rng=rng)
                if "-" in q.prompt:
                    negative_found = True
                    break
        assert negative_found

    def test_practice_session_no_duplicate_prompts(self):
        """Verify that questions do not repeat in a session."""
        outputs = []
        session = PracticeSession(
            topic="derivatives",
            count=5,
            seed=42,
            input_func=lambda _: "skip",
            print_func=outputs.append,
        )
        summary = session.run()
        assert summary["total"] == 5
        assert summary["completed"] == 5
        assert summary["skipped"] == 5

    def test_randint_nonzero_helper(self):
        """Verify randint_nonzero and alias randit_nonzero exclude zero and respect bounds."""
        from mathstore.study.practice import randit_nonzero, randint_nonzero

        rng = random.Random(123)
        for _ in range(50):
            val = randint_nonzero(rng, -5, 5)
            assert val != 0
            assert -5 <= val <= 5

            val_alias = randit_nonzero(rng, -3, 3)
            assert val_alias != 0
            assert -3 <= val_alias <= 3

    def test_integral_exp_generation(self):
        """Verify exponential integrals are properly generated with valid antiderivatives."""
        rng = random.Random(42)
        q = _gen_integral_question("medium", rng)
        assert q.topic == "integrals"
        assert q.question_type == "integral"

    def test_derivative_session_subtype_diversity(self):
        """Verify that a 5-question derivative session generates diverse subtypes without repeats."""
        for seed in [1, 42, 99, 123]:
            session = PracticeSession(
                topic="derivatives",
                count=5,
                seed=seed,
                input_func=lambda _: "skip",
                print_func=lambda *args: None,
            )
            summary = session.run()
            assert summary["total"] == 5

            # Verify that session question generation ensures all 5 subtypes are unique
            rng = random.Random(seed)
            used: set[str] = set()
            subtypes = []
            for _ in range(5):
                q = generate_question(
                    topic="derivatives",
                    difficulty="medium",
                    rng=rng,
                    exclude_subtypes=used,
                )
                used.add(q.subtype)
                subtypes.append(q.subtype)

            assert len(set(subtypes)) == 5, f"Seed {seed} had non-unique subtypes: {subtypes}"
            assert subtypes.count("chain_exp") <= 1


class TestPracticeRefactoredSubmodules:
    """Verifies that the refactored modular practice package and submodules expose expected interfaces."""

    def test_submodule_direct_imports(self):
        """Direct submodule imports should function cleanly without circular dependencies."""
        from mathstore.study.practice.evaluators import (
            _normalize_input_str,
            check_answer,
        )
        from mathstore.study.practice.generators import (
            CANONICAL_TOPICS,
            TOPIC_ALIASES,
            _gen_algebra_question,
            _gen_derivative_question,
            _gen_integral_question,
            _gen_matrix_question,
            _gen_stats_question,
            _randint_nonzero,
            _select_subtype,
            generate_question,
            randit_nonzero,
            randint_nonzero,
        )
        from mathstore.study.practice.models import PracticeQuestion
        from mathstore.study.practice.session import (
            PracticeSession,
            format_question_card,
        )

        assert callable(check_answer)
        assert callable(_normalize_input_str)
        assert callable(generate_question)
        assert callable(randint_nonzero)
        assert callable(_randint_nonzero)
        assert callable(randit_nonzero)
        assert callable(_select_subtype)
        assert callable(_gen_algebra_question)
        assert callable(_gen_derivative_question)
        assert callable(_gen_integral_question)
        assert callable(_gen_matrix_question)
        assert callable(_gen_stats_question)
        assert isinstance(CANONICAL_TOPICS, list)
        assert isinstance(TOPIC_ALIASES, dict)
        assert PracticeQuestion is not None
        assert PracticeSession is not None
        assert callable(format_question_card)

    def test_package_facade_reexports(self):
        """mathstore.study.practice facade should re-export all symbols identically to submodules."""
        import mathstore.study.practice as practice_pkg
        from mathstore.study.practice import evaluators, generators, models, session

        assert practice_pkg.PracticeQuestion is models.PracticeQuestion
        assert practice_pkg.check_answer is evaluators.check_answer
        assert practice_pkg._normalize_input_str is evaluators._normalize_input_str
        assert practice_pkg.generate_question is generators.generate_question
        assert practice_pkg.CANONICAL_TOPICS is generators.CANONICAL_TOPICS
        assert practice_pkg.TOPIC_ALIASES is generators.TOPIC_ALIASES
        assert practice_pkg.randint_nonzero is generators.randint_nonzero
        assert practice_pkg._randint_nonzero is generators._randint_nonzero
        assert practice_pkg.randit_nonzero is generators.randit_nonzero
        assert practice_pkg._select_subtype is generators._select_subtype
        assert practice_pkg.PracticeSession is session.PracticeSession
        assert practice_pkg.format_question_card is session.format_question_card

    def test_top_level_study_reexports(self):
        """mathstore.study facade must maintain backward compatibility for practice symbols."""
        from mathstore.study import (
            CANONICAL_TOPICS,
            PracticeQuestion,
            PracticeSession,
            check_answer,
            format_question_card,
            generate_question,
        )
        from mathstore.study.practice import (
            CANONICAL_TOPICS as PKG_CANONICAL,
            PracticeQuestion as PKG_Question,
            PracticeSession as PKG_Session,
            check_answer as pkg_check,
            format_question_card as pkg_format,
            generate_question as pkg_generate,
        )

        assert CANONICAL_TOPICS is PKG_CANONICAL
        assert PracticeQuestion is PKG_Question
        assert PracticeSession is PKG_Session
        assert check_answer is pkg_check
        assert format_question_card is pkg_format
        assert generate_question is pkg_generate

    def test_all_exports_exist(self):
        """Every symbol listed in __all__ across all practice modules must exist."""
        from mathstore.study.practice import (
            evaluators,
            generators,
            models,
            session,
        )
        import mathstore.study.practice as practice_pkg

        for mod in (practice_pkg, evaluators, generators, models, session):
            assert hasattr(mod, "__all__")
            for symbol_name in mod.__all__:
                assert hasattr(mod, symbol_name), f"{mod.__name__} missing exported symbol {symbol_name}"
