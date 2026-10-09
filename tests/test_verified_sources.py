import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from verified_sources import VerifiedSources
from prepare_overfit import sha


class VerifiedSourcesTests(unittest.TestCase):
    def test_repeated_binding_must_match_first_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'source';p.write_text('original');r=dict(path=str(p),sha256=sha(p));v=VerifiedSources();v.verify(r);v.verify(r)
            with self.assertRaises(ValueError):v.verify(dict(r,sha256='0'*64))
            p.write_text('different')
            with self.assertRaises(ValueError):v.verify(r)

    def test_verification_cannot_be_reused_across_an_input_change(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'source';p.write_text('original');r=dict(path=str(p),sha256=sha(p));v=VerifiedSources();v.verify(r)
            p.write_text('changed');new=dict(path=str(p),sha256=sha(p))
            with self.assertRaises(ValueError):v.verify(new)
            VerifiedSources().verify(new)

    def test_identity_change_during_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'source';p.write_text('original');r=dict(path=str(p),sha256=sha(p))
            with patch('verified_sources.identity',side_effect=[dict(size=8),dict(size=9)]):
                with self.assertRaises(ValueError):VerifiedSources().verify(r)


if __name__=='__main__':unittest.main()
