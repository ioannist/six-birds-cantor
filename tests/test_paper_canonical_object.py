from pathlib import Path


def test_canonical_object_exists_and_contains_required_anchors():
    path = Path("paper/sections/03_canonical_object.tex")
    assert path.exists()
    text = path.read_text()

    for anchor in [
        r"\pi_0",
        r"\pi_1",
        r"\phi:\mathcal{O}_0\to \mathcal{O}_1",
        r"\Hybrid(x)",
    ]:
        assert anchor in text


def test_canonical_object_contains_required_phrases_and_hierarchy():
    text = Path("paper/sections/03_canonical_object.tex").read_text()

    for phrase in [
        "canonical hybrid object",
        "factorization",
        "packaged-object map",
        "strict-extension theoremlet",
        "lawfulness theoremlet",
        "cocycle pressure closure theoremlet",
        "strict theory extension theoremlet",
        "conditional disintegration theoremlet",
    ]:
        assert phrase in text
