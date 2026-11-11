"""Stdlib checks for curated retrieval, key gating, and CORS parsing."""

import os
import unittest

from knowledge_base import retrieve_knowledge
from settings import cors_config, is_llm_configured


class KnowledgeRetrievalTests(unittest.TestCase):
    def test_preset_chunks_are_labeled_illustrative(self):
        chunks = retrieve_knowledge(["ignored"], "biohacker", "ignored")
        self.assertEqual(len(chunks), 3)
        for chunk in chunks:
            self.assertTrue(chunk.startswith("[ILLUSTRATIVE"))
            self.assertIn("to-be-verified", chunk)

    def test_each_preset_returns_its_own_notes(self):
        self.assertIn("CYP3A4", retrieve_knowledge([], "grapefruit")[0])
        self.assertIn("ADH", retrieve_knowledge([], "methanol")[0])
        self.assertIn("Cereblon", retrieve_knowledge([], "thalidomide")[0])

    def test_custom_case_with_no_overlap_returns_nothing(self):
        self.assertEqual(
            retrieve_knowledge([], "custom", "the weather is nice today"),
            [],
        )

    def test_custom_case_matches_grapefruit_keywords(self):
        chunks = retrieve_knowledge(
            [],
            "custom",
            "Patient drinks grapefruit juice while taking atorvastatin",
        )
        self.assertEqual(len(chunks), 1)
        self.assertIn("CYP3A4", chunks[0])
        self.assertTrue(chunks[0].startswith("[ILLUSTRATIVE"))

    def test_custom_case_returns_at_most_three_chunks(self):
        chunks = retrieve_knowledge(
            [],
            "custom",
            "rapamycin metformin semaglutide grapefruit methanol thalidomide",
        )
        self.assertEqual(len(chunks), 3)

    def test_chinese_custom_case_matches_methanol_note(self):
        chunks = retrieve_knowledge([], "custom", "患者误服甲醇后视物模糊")
        self.assertTrue(any("甲醇" in chunk for chunk in chunks))


class SettingsTests(unittest.TestCase):
    def test_placeholder_keys_are_rejected(self):
        for key in ("", "demo-key", "your_api_key_here", "sk-xxxxxxxxxxxxxxxx", "  "):
            self.assertFalse(is_llm_configured(key))

    def test_real_looking_key_is_accepted(self):
        self.assertTrue(is_llm_configured("sk-local-test-not-a-secret"))

    def test_missing_env_is_not_configured(self):
        previous = os.environ.pop("LLM_API_KEY", None)
        try:
            self.assertFalse(is_llm_configured())
        finally:
            if previous is not None:
                os.environ["LLM_API_KEY"] = previous

    def test_default_cors_keeps_local_dev_origins(self):
        origins, credentials = cors_config("")
        # Empty string is not the wildcard; it yields no extra origins.
        self.assertEqual(origins, [])
        self.assertTrue(credentials)
        origins, credentials = cors_config(None if False else (
            "http://localhost:5173, https://bio-house.example"
        ))
        self.assertEqual(
            origins,
            ["http://localhost:5173", "https://bio-house.example"],
        )
        self.assertTrue(credentials)

    def test_wildcard_cors_disables_credentials(self):
        origins, credentials = cors_config("*")
        self.assertEqual(origins, ["*"])
        self.assertFalse(credentials)


if __name__ == "__main__":
    unittest.main()
