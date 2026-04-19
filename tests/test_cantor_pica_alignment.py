import json
import subprocess
import sys
import unittest
from pathlib import Path


EXPECTED_REDUCED = {
    ("P2<-P4", "A10"),
    ("P4<-P4", "A15"),
    ("P4<-P3", "A14"),
    ("P3<-P4", "A19"),
    ("P2<-P6", "A12"),
    ("P5<-P4", "A22"),
    ("P5<-P6", "A23"),
    ("P6<-P6", "A25"),
}


class CantorPicaAlignmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.alignment_path = self.repo_root / "configs" / "pica" / "cantor_pica_alignment_v1.json"

    def test_alignment_validates(self) -> None:
        validate_script = self.repo_root / "scripts" / "validate_metadata.py"
        proc = subprocess.run(
            [sys.executable, str(validate_script), "--pica-alignment", str(self.alignment_path)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

    def test_family_coverage(self) -> None:
        data = json.loads(self.alignment_path.read_text(encoding="utf-8"))
        aligned = {entry["family_id"] for entry in data["family_alignment"]}
        expected = set()
        for config_path in (self.repo_root / "configs" / "experiments").rglob("*.json"):
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
            expected.add(cfg["family_id"])
        self.assertEqual(aligned, expected)

    def test_stage_dependent_marked_control_only(self) -> None:
        data = json.loads(self.alignment_path.read_text(encoding="utf-8"))
        target = None
        for entry in data["family_alignment"]:
            if entry["family_id"] == "contextual_local.stage_dependent_alternating_removal":
                target = entry
                break
        self.assertIsNotNone(target)
        self.assertEqual(target["pica_status"], "control_only")
        self.assertIn("nonautonomous", target["notes"].lower())

    def test_reduced_cell_set_exact(self) -> None:
        data = json.loads(self.alignment_path.read_text(encoding="utf-8"))
        reduced = {(entry["cell"], entry["code"]) for entry in data["reduced_cell_set"]}
        self.assertEqual(reduced, EXPECTED_REDUCED)


if __name__ == "__main__":
    unittest.main()
