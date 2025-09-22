 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/src/packing_list_translator/cli.py
index 0000000000000000000000000000000000000000..1be15f292483ab6a07ed65a2ac84cd9e488dee39 100644
--- a//dev/null
+++ b/src/packing_list_translator/cli.py
@@ -0,0 +1,66 @@
+"""Command line interface for translating Excel workbooks."""
+
+from __future__ import annotations
+
+import argparse
+import sys
+from pathlib import Path
+
+from .excel_translator import ExcelTranslator, TranslationError
+
+
+def _build_parser() -> argparse.ArgumentParser:
+    parser = argparse.ArgumentParser(
+        description=(
+            "Translate the textual contents of an Excel workbook into the target language."
+        )
+    )
+    parser.add_argument("input", type=Path, help="Path to the source Excel (.xlsx) file.")
+    parser.add_argument(
+        "output",
+        type=Path,
+        help="Destination path for the translated workbook.",
+    )
+    parser.add_argument(
+        "--source",
+        default="auto",
+        help="Language code to translate from (default: automatic detection).",
+    )
+    parser.add_argument(
+        "--target",
+        default="en",
+        help="Language code to translate into (default: en).",
+    )
+    parser.add_argument(
+        "--batch-size",
+        type=int,
+        default=25,
+        help="Number of cells to translate per network request (default: 25).",
+    )
+    return parser
+
+
+def main(argv: list[str] | None = None) -> None:
+    parser = _build_parser()
+    args = parser.parse_args(argv)
+
+    translator = ExcelTranslator(
+        source_language=args.source,
+        target_language=args.target,
+        batch_size=args.batch_size,
+    )
+
+    try:
+        translator.translate_workbook(args.input, args.output)
+    except FileNotFoundError:
+        parser.exit(status=2, message=f"Input workbook '{args.input}' does not exist.\n")
+    except TranslationError as exc:
+        parser.exit(status=1, message=f"Translation failed: {exc}.\n")
+    except Exception as exc:  # pragma: no cover - defensive
+        parser.exit(status=1, message=f"Unexpected error: {exc}.\n")
+    else:
+        sys.stdout.write(f"Translated workbook saved to {args.output}\n")
+
+
+if __name__ == "__main__":  # pragma: no cover
+    main()
 
EOF
)
