 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/src/packing_list_translator/__init__.py
index 0000000000000000000000000000000000000000..6858080be0dee4a5138fd5fb2b9014eb2670e37c 100644
--- a//dev/null
+++ b/src/packing_list_translator/__init__.py
@@ -0,0 +1,5 @@
+"""Utilities for translating Excel workbooks into English."""
+
+from .excel_translator import ExcelTranslator, TranslationError
+
+__all__ = ["ExcelTranslator", "TranslationError"]
 
EOF
)
