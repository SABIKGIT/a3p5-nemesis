"""Optional analysis execution in a disposable directory, preserving the archive."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from common import ANALYSIS, NumericCase, rows


@unittest.skipUnless(os.environ.get("A3P5_VERIFY_ENGINEERING") == "1",
                     "opt in with --regenerate-engineering (plotting dependencies required)")
class EngineeringRegenerationTests(NumericCase):
    def test_script_recreates_all_numerical_tables_in_scratch_space(self):
        with tempfile.TemporaryDirectory(prefix="a3p5-engineering-") as temporary:
            analysis = Path(temporary) / "analysis"
            analysis.mkdir()
            script = analysis / "engineering_analysis.py"
            shutil.copy2(ANALYSIS / script.name, script)
            completed = subprocess.run([sys.executable, str(script)], cwd=temporary,
                                       capture_output=True, text=True, timeout=180)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            expected_files = sorted((ANALYSIS / "tables").glob("*.csv"))
            self.assertEqual(len(expected_files), 9)
            self.assertEqual({p.name for p in (analysis / "tables").glob("*.csv")}, {p.name for p in expected_files})
            for archived in expected_files:
                expected, actual = rows(archived), rows(analysis / "tables" / archived.name)
                self.assertEqual(len(actual), len(expected), archived.name)
                for saved, regenerated in zip(expected, actual):
                    self.assertEqual(saved.keys(), regenerated.keys())
                    for key in saved:
                        try:
                            x, y = float(regenerated[key]), float(saved[key])
                        except ValueError:
                            self.assertEqual(regenerated[key], saved[key])
                        else:
                            self.assertClose(x, y, context=archived.name + ":" + key)
            self.assertEqual(len(list((analysis / "figures").glob("*.png"))), 8)
            self.assertEqual(len(list((analysis / "figures").glob("*.svg"))), 8)
