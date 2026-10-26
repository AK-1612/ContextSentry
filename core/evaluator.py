# core/evaluator.py
import ast
from typing import Dict, Any

class ComplexityVisitor(ast.NodeVisitor):
    """Calculates Cyclomatic Complexity by counting control flow decision branches."""
    def __init__(self):
        self.complexity = 1  # Base complexity score

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


def evaluate_gate(content: str, line_threshold: int = 350, complexity_threshold: int = 15) -> Dict[str, Any]:
    lines = content.splitlines()
    line_count = len(lines)

    complexity = 1
    try:
        tree = ast.parse(content)
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        complexity = visitor.complexity
    except SyntaxError:
        # Graceful fallback for non-Python or syntax-incomplete files
        complexity = 1

    should_gate = (line_count > line_threshold) or (complexity > complexity_threshold)

    return {
        "should_gate": should_gate,
        "line_count": line_count,
        "complexity": complexity,
        "reason": f"Lines: {line_count}/{line_threshold}, Complexity: {complexity}/{complexity_threshold}"
    }