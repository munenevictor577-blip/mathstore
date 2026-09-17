import pytest

from mathstore.reference import (
    REFERENCE_TOPICS,
    get_reference,
    list_topics,
    list_topics_formatted,
)


def test_list_topics():
    """Verify dictionary of available study topics."""
    topics = list_topics()
    assert "derivatives" in topics
    assert "integrals" in topics
    assert "trig" in topics
    assert "limits" in topics
    assert "series" in topics
    assert len(topics) == len(REFERENCE_TOPICS)


def test_list_topics_formatted():
    """Verify formatted topic listing string."""
    formatted = list_topics_formatted()
    assert "Available study reference topics:" in formatted
    assert "derivatives" in formatted
    assert "Usage: mathstore ref <topic> [--latex]" in formatted


@pytest.mark.parametrize(
    "topic,expected_substring",
    [
        ("derivatives", "Power Rule"),
        ("integrals", "By Parts"),
        ("trig", "Pythagorean Identities"),
        ("limits", "L'Hôpital's Rule"),
        ("series", "Maclaurin Series"),
    ],
)
def test_get_reference_text(topic: str, expected_substring: str):
    """Verify text reference sheet content."""
    content = get_reference(topic, latex=False)
    assert expected_substring in content


@pytest.mark.parametrize(
    "topic",
    ["derivatives", "integrals", "trig", "limits", "series"],
)
def test_get_reference_latex(topic: str):
    """Verify LaTeX reference sheet content contains valid LaTeX markup."""
    content = get_reference(topic, latex=True)
    assert r"\section*" in content
    assert "\\" in content


@pytest.mark.parametrize(
    "alias,canonical",
    [
        ("derivative", "derivatives"),
        ("diff", "derivatives"),
        ("integral", "integrals"),
        ("int", "integrals"),
        ("integrate", "integrals"),
        ("trigonometry", "trig"),
        ("identities", "trig"),
        ("limit", "limits"),
        ("taylor", "series"),
        ("maclaurin", "series"),
    ],
)
def test_get_reference_aliases(alias: str, canonical: str):
    """Verify topic aliases resolve to the same canonical reference sheet."""
    assert get_reference(alias) == get_reference(canonical)


def test_get_reference_unknown_topic():
    """Verify ValueError is raised when requesting an unknown reference topic."""
    with pytest.raises(ValueError, match="Unknown reference topic 'quantum'"):
        get_reference("quantum")
