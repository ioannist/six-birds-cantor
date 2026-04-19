import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class SmokeTest(unittest.TestCase):
    def test_package_import_and_version(self) -> None:
        import contextual_cantor

        self.assertTrue(hasattr(contextual_cantor, "__version__"))
        self.assertIsInstance(contextual_cantor.__version__, str)
        self.assertTrue(contextual_cantor.__version__.strip())


if __name__ == "__main__":
    unittest.main()
