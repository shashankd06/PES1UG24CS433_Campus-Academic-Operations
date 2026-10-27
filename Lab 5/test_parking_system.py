"""Regression tests for permit validation, expiry and persistence."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta

import parking_system as parking


class PermitTests(unittest.TestCase):
    """Exercise externally observable permit behavior."""

    def setUp(self):
        parking.PERMITS.clear()
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.file = Path(self.directory.name) / 'permits.json'

    def test_registration(self):
        records = []
        identifier = parking.register_permit('KA01AB1234', 'A', records)
        self.assertTrue(identifier.startswith('P'))
        self.assertEqual(records, [('KA01AB1234', 'A')])
        self.assertEqual(parking.PERMITS['KA01AB1234']['expiry'],
                         (date.today() + timedelta(days=180)).isoformat())

    def test_invalid_plates_do_not_mutate_database(self):
        for plate in ('', '   ', None, 123):
            with self.subTest(plate=plate), self.assertRaises(ValueError):
                parking.register_permit(plate, 'A')
        self.assertEqual(parking.PERMITS, {})

    def test_invalid_zone(self):
        with self.assertRaises(ValueError):
            parking.register_permit('KA01AB1234', 'Z')
        self.assertEqual(parking.PERMITS, {})

    def test_records_are_opt_in(self):
        records = []
        parking.register_permit('ONE', 'A', records)
        parking.register_permit('TWO', 'B')
        self.assertEqual(records, [('ONE', 'A')])
        self.assertIsNone(parking.register_permit.__defaults__[0])

    def test_identifiers_differ(self):
        first = parking.register_permit('ONE', 'A')
        second = parking.register_permit('TWO', 'A')
        self.assertNotEqual(first, second)

    def test_unknown_revocation(self):
        parking.register_permit('ONE', 'A')
        parking.revoke_permit('MISSING')
        self.assertIn('ONE', parking.PERMITS)

    def test_known_revocation(self):
        parking.register_permit('ONE', 'A')
        parking.revoke_permit('ONE')
        self.assertNotIn('ONE', parking.PERMITS)

    def test_past_expiry(self):
        parking.register_permit('ONE', 'A')
        parking.set_expiry('ONE', '2020-01-01')
        self.assertTrue(parking.is_expired('ONE'))

    def test_today_remains_valid(self):
        parking.register_permit('ONE', 'A')
        parking.set_expiry('ONE', date.today().isoformat())
        self.assertFalse(parking.is_expired('ONE'))

    def test_bad_expiry_fails_closed(self):
        parking.register_permit('ONE', 'A')
        parking.PERMITS['ONE']['expiry'] = '01/01/2020'
        self.assertTrue(parking.is_expired('ONE'))
        self.assertTrue(parking.is_expired('MISSING'))

    def test_invalid_expiry_update_preserves_record(self):
        parking.register_permit('ONE', 'A')
        old = parking.PERMITS['ONE']['expiry']
        for invalid in ('01/01/2020', '2020-02-30', '20200101', None):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                parking.set_expiry('ONE', invalid)
        self.assertEqual(parking.PERMITS['ONE']['expiry'], old)

    def test_zone_scan(self):
        parking.register_permit('VALID', 'A')
        parking.register_permit('WRONG', 'B')
        parking.register_permit('OLD', 'A')
        parking.set_expiry('OLD', '2020-01-01')
        self.assertEqual(parking.scan_zone('A', ['VALID', 'WRONG', 'OLD', 'NO']),
                         ['WRONG', 'OLD', 'NO'])

    def test_invalid_scan_zone(self):
        with self.assertRaises(ValueError):
            parking.scan_zone('Z', [])

    def test_save_and_load(self):
        parking.register_permit('ONE', 'C')
        expected = dict(parking.PERMITS)
        parking.save_permit_database(self.file)
        parking.PERMITS.clear()
        parking.load_permit_database(self.file)
        self.assertEqual(parking.PERMITS, expected)

    def test_missing_file(self):
        parking.register_permit('ONE', 'A')
        parking.load_permit_database(self.file)
        self.assertEqual(parking.PERMITS, {})

    def test_corrupt_json_preserves_memory_and_disk(self):
        parking.register_permit('ONE', 'A')
        self.file.write_text('{broken', encoding='utf-8')
        with self.assertRaises(json.JSONDecodeError):
            parking.load_permit_database(self.file)
        self.assertIn('ONE', parking.PERMITS)
        self.assertEqual(self.file.read_text(encoding='utf-8'), '{broken')

    def test_bad_database_schema_preserves_memory(self):
        parking.register_permit('ONE', 'A')
        for invalid in ([], {'TWO': {}}, {'TWO': None},
                        {'TWO': {'zone': 'Z', 'permit': 'P1',
                                 'expiry': '2020-01-01'}}):
            self.file.write_text(json.dumps(invalid), encoding='utf-8')
            with self.subTest(database=invalid), self.assertRaises(ValueError):
                parking.load_permit_database(self.file)
            self.assertIn('ONE', parking.PERMITS)

    def test_import_has_no_interactive_side_effects(self):
        script = Path(parking.__file__).resolve()
        result = subprocess.run(
            [sys.executable, '-c',
             'import importlib.util; '
             f's=importlib.util.spec_from_file_location("subject", {str(script)!r}); '
             'm=importlib.util.module_from_spec(s); s.loader.exec_module(m)'],
            cwd=self.directory.name, input='', capture_output=True, text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertFalse(self.file.exists())


if __name__ == '__main__':
    unittest.main()
