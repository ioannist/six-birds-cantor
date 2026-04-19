import math
import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from contextual_cantor.classical_similarity import (
    generate_cylinders,
    maps_from_restricted_digits,
    solve_similarity_dimension,
)


class ClassicalSimilarityTest(unittest.TestCase):
    def test_middle_thirds_dimension(self) -> None:
        maps = maps_from_restricted_digits(base=3, allowed_digits=[0, 2])
        computed = solve_similarity_dimension([m.ratio for m in maps], tol=1e-14)
        exact = math.log(2.0) / math.log(3.0)
        self.assertLessEqual(abs(computed - exact), 1e-12)

    def test_base4_02_dimension(self) -> None:
        maps = maps_from_restricted_digits(base=4, allowed_digits=[0, 2])
        computed = solve_similarity_dimension([m.ratio for m in maps], tol=1e-14)
        exact = math.log(2.0) / math.log(4.0)
        self.assertLessEqual(abs(computed - exact), 1e-12)

    def test_base5_024_dimension(self) -> None:
        maps = maps_from_restricted_digits(base=5, allowed_digits=[0, 2, 4])
        computed = solve_similarity_dimension([m.ratio for m in maps], tol=1e-14)
        exact = math.log(3.0) / math.log(5.0)
        self.assertLessEqual(abs(computed - exact), 1e-12)

    def test_cylinder_counts(self) -> None:
        maps2 = maps_from_restricted_digits(base=3, allowed_digits=[0, 2])
        cylinders2 = generate_cylinders(maps2, depth=4)
        self.assertEqual(len(cylinders2), 2**4)

        maps3 = maps_from_restricted_digits(base=5, allowed_digits=[0, 2, 4])
        cylinders3 = generate_cylinders(maps3, depth=3)
        self.assertEqual(len(cylinders3), 3**3)
        for start, end in cylinders3:
            self.assertGreaterEqual(start, 0.0)
            self.assertLessEqual(end, 1.0)
            self.assertLessEqual(start, end)


if __name__ == "__main__":
    unittest.main()
