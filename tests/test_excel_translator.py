 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/tests/test_excel_translator.py
index 0000000000000000000000000000000000000000..ca2b7b2098b0d375388b3c2045f57e13972ee073 100644
--- a//dev/null
+++ b/tests/test_excel_translator.py
@@ -0,0 +1,64 @@
+from pathlib import Path
+
+from openpyxl import Workbook, load_workbook
+
+from packing_list_translator import ExcelTranslator
+
+
+class DummyResult:
+    def __init__(self, text: str):
+        self.text = text
+
+
+class DummyTranslator:
+    def __init__(self):
+        self.calls: list[list[str]] = []
+
+    def translate(self, texts, src="auto", dest="en"):
+        if isinstance(texts, str):
+            texts = [texts]
+        chunk = list(texts)
+        self.calls.append(chunk)
+        return [DummyResult(f"{text}_en") for text in chunk]
+
+
+def build_workbook(path: Path) -> None:
+    workbook = Workbook()
+    sheet = workbook.active
+    sheet.title = "Datos"
+    sheet["A1"] = "Hola"
+    sheet["A2"] = 123
+    sheet["B1"] = "Bonjour"
+    sheet["B2"] = ""
+    sheet["C1"] = "=SUM(A2:A3)"
+
+    second_sheet = workbook.create_sheet("Notas")
+    second_sheet["A1"] = "こんにちは"
+    second_sheet["B1"] = None
+
+    workbook.save(path)
+
+
+def test_translate_workbook(tmp_path):
+    input_path = tmp_path / "input.xlsx"
+    output_path = tmp_path / "output.xlsx"
+    build_workbook(input_path)
+
+    translator = ExcelTranslator(translator=DummyTranslator(), batch_size=2)
+    translator.translate_workbook(input_path, output_path)
+
+    output_workbook = load_workbook(output_path)
+
+    datos = output_workbook["Datos"]
+    assert datos["A1"].value == "Hola_en"
+    assert datos["B1"].value == "Bonjour_en"
+    assert datos["A2"].value == 123
+    assert datos["B2"].value in {"", None}
+    assert datos["C1"].value == "=SUM(A2:A3)"
+
+    notas = output_workbook["Notas"]
+    assert notas["A1"].value == "こんにちは_en"
+    assert notas["B1"].value is None
+
+    dummy_calls = translator._translator.calls  # type: ignore[attr-defined]
+    assert dummy_calls == [["Hola", "Bonjour"], ["こんにちは"]]
 
EOF
)
