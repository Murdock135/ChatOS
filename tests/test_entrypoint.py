from pathlib import Path
import tempfile
import unittest
from System.Scripts.install_entrypoint import install


class EntryTests(unittest.TestCase):
    def test_reversible_install_is_idempotent_and_preserves_existing_guidance(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();vault=root/'vault';codex=root/'codex';skills=root/'skills'
            source=vault/'System/Skills/chief-of-staff-entry/SKILL.md'
            source.parent.mkdir(parents=True);source.write_text('---\nname: chief-of-staff-entry\ndescription: Test\n---\n')
            codex.mkdir();instructions=codex/'AGENTS.md';instructions.write_text('Existing user guidance\n')
            self.assertTrue(install(vault,codex,skills)['instructions_changed'])
            first=instructions.read_text()
            self.assertTrue(first.startswith('Existing user guidance\n'))
            self.assertFalse(install(vault,codex,skills)['instructions_changed'])
            self.assertEqual(instructions.read_text(),first)
            backups=list((vault/'System/Backups/entrypoint-install').glob('*/AGENTS.original.md'))
            self.assertEqual(len(backups),1)
            self.assertEqual(backups[0].read_text(),'Existing user guidance\n')
            (skills/'chief-of-staff-entry/SKILL.md').write_text('User edited installed skill')
            with self.assertRaises(ValueError):install(vault,codex,skills)
            self.assertEqual(instructions.read_text(),first)


if __name__=='__main__':unittest.main()
