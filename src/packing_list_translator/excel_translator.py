 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/src/packing_list_translator/excel_translator.py
index 0000000000000000000000000000000000000000..69a44c036ab10d990cb7a47fb57dd1573c2f79b2 100644
--- a//dev/null
+++ b/src/packing_list_translator/excel_translator.py
@@ -0,0 +1,148 @@
+"""Core translation utilities for Excel workbooks."""
+
+from __future__ import annotations
+
+from pathlib import Path
+from typing import Iterable, List, Sequence, Tuple, Union
+
+from openpyxl import Workbook, load_workbook
+from openpyxl.worksheet.worksheet import Worksheet
+
+
+class TranslationError(RuntimeError):
+    """Raised when a translation request fails."""
+
+
+class ExcelTranslator:
+    """Translate the textual content of Excel workbooks into another language.
+
+    Parameters
+    ----------
+    translator:
+        Optional object implementing ``translate(texts, src, dest)``. When not
+        provided a :class:`googletrans.Translator` instance is created on demand.
+    source_language:
+        The language code to translate from. Defaults to ``"auto"`` to enable
+        automatic language detection.
+    target_language:
+        The language code to translate into. Defaults to English (``"en"``).
+    batch_size:
+        Number of cells to translate per request to the translation backend.
+    """
+
+    def __init__(
+        self,
+        *,
+        translator=None,
+        source_language: str = "auto",
+        target_language: str = "en",
+        batch_size: int = 25,
+    ) -> None:
+        if batch_size <= 0:
+            raise ValueError("batch_size must be a positive integer")
+
+        if translator is None:
+            try:
+                from googletrans import Translator as GoogleTranslator
+            except ModuleNotFoundError as exc:  # pragma: no cover - defensive
+                raise RuntimeError(
+                    "googletrans is not installed. Install the package or pass "
+                    "a custom translator implementation."
+                ) from exc
+            translator = GoogleTranslator()
+
+        self._translator = translator
+        self.source_language = source_language
+        self.target_language = target_language
+        self.batch_size = batch_size
+
+    def translate_workbook(
+        self, input_path: Union[str, Path], output_path: Union[str, Path]
+    ) -> None:
+        """Translate every sheet in *input_path* and write the result to *output_path*."""
+
+        input_path = Path(input_path)
+        output_path = Path(output_path)
+
+        workbook = load_workbook(filename=input_path, data_only=False)
+
+        translated_workbook = Workbook()
+        # Remove the default sheet created by openpyxl so we can mirror the source.
+        if translated_workbook.worksheets:
+            default_sheet = translated_workbook.worksheets[0]
+            translated_workbook.remove(default_sheet)
+
+        for sheet in workbook.worksheets:
+            translated_sheet = translated_workbook.create_sheet(title=sheet.title)
+            positions, texts = self._copy_sheet_collect_strings(sheet, translated_sheet)
+            translations = self._translate_texts(texts)
+            for (row, column), translation in zip(positions, translations):
+                translated_sheet.cell(row=row, column=column, value=translation)
+
+            # Preserve merged-cell ranges to keep layout roughly intact.
+            for merged_range in sheet.merged_cells.ranges:
+                translated_sheet.merge_cells(str(merged_range))
+
+        translated_workbook.save(output_path)
+
+    def _copy_sheet_collect_strings(
+        self, source_sheet: Worksheet, target_sheet: Worksheet
+    ) -> Tuple[List[Tuple[int, int]], List[str]]:
+        positions: List[Tuple[int, int]] = []
+        texts: List[str] = []
+
+        for row in source_sheet.iter_rows():
+            for cell in row:
+                target_sheet.cell(row=cell.row, column=cell.column, value=cell.value)
+                if self._should_translate(cell.value, cell.data_type):
+                    positions.append((cell.row, cell.column))
+                    texts.append(str(cell.value))
+
+        return positions, texts
+
+    @staticmethod
+    def _should_translate(value, data_type: str) -> bool:
+        if not isinstance(value, str):
+            return False
+        if data_type == "f":  # skip formulas
+            return False
+        stripped = value.strip()
+        if not stripped:
+            return False
+        if stripped.isdigit():
+            return False
+        return True
+
+    def _translate_texts(self, texts: Sequence[str]) -> List[str]:
+        if not texts:
+            return []
+
+        translated: List[str] = []
+        for start in range(0, len(texts), self.batch_size):
+            chunk = list(texts[start : start + self.batch_size])
+            try:
+                result = self._translator.translate(
+                    chunk, src=self.source_language, dest=self.target_language
+                )
+            except Exception as exc:  # pragma: no cover - defensive
+                raise TranslationError("Translation service failed") from exc
+
+            translated.extend(self._normalise_results(result))
+
+        return translated
+
+    @staticmethod
+    def _normalise_results(result: Union[Iterable, object]) -> List[str]:
+        if isinstance(result, Iterable) and not isinstance(result, (str, bytes)):
+            return [ExcelTranslator._extract_text(item) for item in result]
+        return [ExcelTranslator._extract_text(result)]
+
+    @staticmethod
+    def _extract_text(item: object) -> str:
+        if hasattr(item, "text"):
+            text = getattr(item, "text")
+            if text is None:
+                raise TranslationError("Translation result missing text")
+            return text
+        return str(item)
+
 
EOF
)
