"""
MultiGravity Diagnostic and Smoke Test Suite
Verifies cross-platform AI detection, path resolutions, and profile validators.
"""
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import main

# Close any GUI root created during import
if hasattr(main, "janela") and main.janela:
    try:
        main.janela.destroy()
    except Exception:
        pass

class TestMultiGravityBridge(unittest.TestCase):
    def test_encode_claude_project_dir(self):
        path = r"C:\Users\test\project"
        encoded = main.encode_claude_project_dir(path)
        self.assertNotIn(":", encoded)
        self.assertNotIn("\\", encoded)
        self.assertIn("project", encoded)

    def test_clean_user_text(self):
        raw = "<USER_REQUEST>Hello World!</USER_REQUEST><ADDITIONAL_METADATA>meta</ADDITIONAL_METADATA>"
        cleaned = main.clean_user_text(raw)
        self.assertEqual(cleaned, "Hello World!")

    def test_validar_nome_perfil(self):
        self.assertTrue(main.validar_nome_perfil("Perfil_Trabalho"))
        self.assertTrue(main.validar_nome_perfil("Dev-123"))
        self.assertFalse(main.validar_nome_perfil("Perfil/Invalido"))
        self.assertFalse(main.validar_nome_perfil("Perfil:Invalido"))
        self.assertFalse(main.validar_nome_perfil("Perfil."))
        self.assertFalse(main.validar_nome_perfil(""))

    def test_detection_functions_return_bool(self):
        self.assertIsInstance(main.is_claude_installed(), bool)
        self.assertIsInstance(main.is_chatgpt_installed(), bool)

    def test_antigravity_exe_resolution(self):
        exe = main.get_antigravity_exe()
        self.assertIsInstance(exe, str)
        self.assertTrue(exe.endswith(".exe"))

if __name__ == "__main__":
    unittest.main()
