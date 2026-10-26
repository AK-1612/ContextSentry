# core/symbol_indexer.py
import ast
from typing import Dict, List, Any

class ASTSymbolExtractor(ast.NodeVisitor):
    """Extracts classes and functions with exact line ranges."""
    def __init__(self):
        self.symbols: List[Dict[str, Any]] = []

    def visit_FunctionDef(self, node):
        self.symbols.append({
            "type": "function",
            "name": node.name,
            "start_line": node.lineno,
            "end_line": getattr(node, 'end_lineno', node.lineno)
        })
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.symbols.append({
            "type": "class",
            "name": node.name,
            "start_line": node.lineno,
            "end_line": getattr(node, 'end_lineno', node.lineno)
        })
        self.generic_visit(node)

def build_symbol_table(content: str) -> List[Dict[str, Any]]:
    try:
        tree = ast.parse(content)
        extractor = ASTSymbolExtractor()
        extractor.visit(tree)
        return extractor.symbols
    except Exception:
        return []