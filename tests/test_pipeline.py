import unittest

from audio_protocol.memory import DomainMemory
from audio_protocol.pipeline import Orchestrator


class PipelineTest(unittest.TestCase):
    def test_orchestrator_extracts_critical_numbers_and_traceability(self) -> None:
        transcript = (
            "[00:00:01] Alice: We agreed on 2.5 mg/mL for sample A.\n"
            "[00:00:02] Bob: Action: verify stability by 2026-09-01.\n"
        )
        protocol = Orchestrator().run(
            transcript=transcript,
            project="Test Project",
            source_file="/tmp/transcript.txt",
            memory=DomainMemory(glossary={"concentration": "mg/mL"}),
        )

        self.assertTrue(protocol.critical_numbers)
        cn = protocol.critical_numbers[0]
        self.assertEqual(cn.unit, "mg/mL")
        self.assertEqual(cn.speaker, "Alice")
        self.assertEqual(cn.timestamp, "00:00:01")
        self.assertTrue(cn.source_quote)
        self.assertGreaterEqual(cn.confidence, 0)
        self.assertLessEqual(cn.confidence, 1)
        self.assertTrue(protocol.action_items)


if __name__ == "__main__":
    unittest.main()
