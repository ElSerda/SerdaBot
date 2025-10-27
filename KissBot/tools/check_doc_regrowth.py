#!/usr/bin/env python3
"""
🛡️ CI Anti-Regonflage Documentation
Garde-fou pour empêcher la re-accumulation de documentation inline excessive.
"""
import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Seuils KISS adaptés au chaos KissBot
MAX_DOCSTRING_LINES = 8
MAX_DOC_RATIO = 30.0  # 30% max de doc par fichier
MAX_TOTAL_DOC_LINES = 100  # Max doc cumulée par fichier
QUANTUM_TERMS_LIMIT = 3  # Max termes quantiques par docstring

# Termes quantiques à surveiller
QUANTUM_TERMS = [
    'quantum', 'superposition', 'collapse', 'intrication', 'décohérence', 
    'paradigme', 'boson', 'particule', 'observateur', 'métaphore'
]

class DocRegrowthDetector:
    """Détecteur de regonflage documentaire."""
    
    def __init__(self):
        self.violations = []
        self.warnings = []
        self.total_files_checked = 0
        self.total_doc_lines = 0
    
    def check_file(self, file_path: Path) -> bool:
        """Vérifie un fichier Python pour violations doc."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # Statistiques globales
            lines = content.split('\n')
            total_lines = len(lines)
            self.total_files_checked += 1
            
            # Compter documentation
            doc_lines = self._count_doc_lines(content)
            self.total_doc_lines += doc_lines
            
            # Calculer ratio
            doc_ratio = (doc_lines / total_lines) * 100 if total_lines > 0 else 0
            
            # Vérifications
            violations_found = False
            
            # 1. Ratio global excessif
            if doc_ratio > MAX_DOC_RATIO:
                self.violations.append(
                    f"❌ {file_path}: Doc ratio {doc_ratio:.1f}% > {MAX_DOC_RATIO}%"
                )
                violations_found = True
            
            # 2. Trop de doc cumulée
            if doc_lines > MAX_TOTAL_DOC_LINES:
                self.violations.append(
                    f"❌ {file_path}: {doc_lines} doc lines > {MAX_TOTAL_DOC_LINES}"
                )
                violations_found = True
            
            # 3. Vérifier chaque docstring individuellement
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                    docstring = ast.get_docstring(node, clean=False)
                    if docstring:
                        violations_found |= self._check_docstring(docstring, file_path, node)
            
            return not violations_found
            
        except Exception as e:
            self.warnings.append(f"⚠️ {file_path}: Error parsing - {e}")
            return True  # Ne pas bloquer sur erreurs de parsing
    
    def _count_doc_lines(self, content: str) -> int:
        """Compte les lignes de documentation."""
        lines = content.split('\n')
        doc_lines = 0
        in_docstring = False
        
        for line in lines:
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring
                doc_lines += 1
            elif in_docstring:
                doc_lines += 1
        
        return doc_lines
    
    def _check_docstring(self, docstring: str, file_path: Path, node) -> bool:
        """Vérifie une docstring individuelle."""
        violations_found = False
        lines = docstring.split('\n')
        node_name = getattr(node, 'name', 'module')
        
        # 1. Longueur excessive
        if len(lines) > MAX_DOCSTRING_LINES:
            self.violations.append(
                f"❌ {file_path}:{node_name}: Docstring {len(lines)} lines > {MAX_DOCSTRING_LINES}"
            )
            violations_found = True
        
        # 2. Termes quantiques excessifs
        quantum_count = sum(1 for term in QUANTUM_TERMS if term in docstring.lower())
        if quantum_count > QUANTUM_TERMS_LIMIT:
            self.violations.append(
                f"❌ {file_path}:{node_name}: {quantum_count} quantum terms > {QUANTUM_TERMS_LIMIT}"
            )
            violations_found = True
        
        # 3. Détection de patterns suspects
        suspect_patterns = [
            ('🎮🔬', 'Emoji quantique suspect'),
            ('PHÉNOMÈNES QUANTIQUES', 'Section paradigme détectée'),
            ('WORKFLOW QUANTIQUE', 'Workflow détaillé détecté'),
            ('├──', 'Arbre ASCII détecté'),
            ('ANALOGIE PARFAITE', 'Métaphore excessive'),
        ]
        
        for pattern, desc in suspect_patterns:
            if pattern in docstring:
                self.warnings.append(
                    f"⚠️ {file_path}:{node_name}: {desc} - Possible regrowth"
                )
        
        return violations_found
    
    def generate_report(self) -> str:
        """Génère rapport de vérification."""
        report = ["🛡️ CI ANTI-REGONFLAGE REPORT"]
        report.append("=" * 50)
        report.append(f"📊 Files checked: {self.total_files_checked}")
        report.append(f"📝 Total doc lines: {self.total_doc_lines}")
        report.append("")
        
        if not self.violations and not self.warnings:
            report.append("✅ NO DOCUMENTATION REGROWTH DETECTED!")
            report.append("🎯 KISS principles maintained.")
        else:
            if self.violations:
                report.append(f"❌ VIOLATIONS FOUND: {len(self.violations)}")
                report.extend(self.violations)
                report.append("")
            
            if self.warnings:
                report.append(f"⚠️ WARNINGS: {len(self.warnings)}")
                report.extend(self.warnings[:10])  # Limiter warnings
                if len(self.warnings) > 10:
                    report.append(f"... and {len(self.warnings) - 10} more warnings")
        
        return "\n".join(report)

def main():
    """Point d'entrée principal du CI."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("🛡️ CI Anti-Regonflage Documentation")
        print("Usage: python check_doc_regrowth.py [directory]")
        print("Checks for documentation regrowth in Python files.")
        return
    
    # Déterminer répertoire à scanner
    scan_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    
    print(f"🔍 Scanning {scan_dir} for documentation regrowth...")
    
    detector = DocRegrowthDetector()
    
    # Scanner tous les fichiers Python
    python_files = list(scan_dir.rglob("*.py"))
    excluded_patterns = ["__pycache__", ".venv", "venv", "env", "build", ".git", "dist", "backup", ".mypy_cache", "kissbot-venv"]
    
    for py_file in python_files:
        # Exclure certains répertoires
        if any(pattern in str(py_file) for pattern in excluded_patterns):
            continue
        
        detector.check_file(py_file)
    
    # Générer et afficher rapport
    report = detector.generate_report()
    print(report)
    
    # Exit code pour CI
    if detector.violations:
        print(f"\n💥 CI FAILED: {len(detector.violations)} violations found!")
        print("🧹 Action required: Reduce inline documentation or move to docs/")
        sys.exit(1)
    else:
        print("\n✅ CI PASSED: No documentation regrowth detected!")
        sys.exit(0)

if __name__ == "__main__":
    main()