#!/usr/bin/env python3
"""
🧹 Great Documentation Migration Tool
Extraction des docstrings romans vers documentation externe.
Adaptée au cas spécial KissBot avec sur-ingénierie documentaire massive.
"""
import ast
import os
import pathlib
import textwrap
import re

ROOT = pathlib.Path(".")
DOCS = ROOT / "docs" / "api"
DOCS.mkdir(parents=True, exist_ok=True)

# Seuils adaptés au chaos KissBot
MAX_DOCSTRING_LINES = 10
QUANTUM_TERMS = ['quantum', 'superposition', 'collapse', 'intrication', 'décohérence', 'paradigme', 'boson', 'particule']

def extract_module(path: pathlib.Path):
    """Extraire docstrings et analyser le contenu quantique."""
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        module_doc = ast.get_docstring(tree, clean=False) or ""
        
        items = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                doc = ast.get_docstring(node, clean=False) or ""
                if doc.strip():
                    kind = "class" if isinstance(node, ast.ClassDef) else "func"
                    
                    # Analyse quantique
                    quantum_count = sum(1 for term in QUANTUM_TERMS if term in doc.lower())
                    doc_lines = len(doc.split('\n'))
                    
                    items.append({
                        'kind': kind,
                        'name': node.name,
                        'doc': doc,
                        'quantum_terms': quantum_count,
                        'doc_lines': doc_lines,
                        'is_over_engineered': doc_lines > MAX_DOCSTRING_LINES or quantum_count > 3
                    })
        
        return module_doc, items, src
    except Exception as e:
        print(f"❌ Erreur parsing {path}: {e}")
        return "", [], ""

def md_escape(text: str) -> str:
    """Escape markdown problématique."""
    return text.replace("```", "``\\`").replace("# ", "\\# ")

def to_anchor(name: str) -> str:
    """Convertir nom en ancre markdown."""
    return name.lower().replace("_", "-")

def create_stub_docstring(name: str, md_path: str, is_over_engineered: bool) -> str:
    """Créer docstring stub selon complexité."""
    if is_over_engineered:
        return f'"""Over-engineered docs migrated → see: {md_path}#{to_anchor(name)}"""'
    else:
        return f'"""See documentation: {md_path}#{to_anchor(name)}"""'

def migrate_file(py_path: pathlib.Path):
    """Migrer un fichier Python vers documentation externe."""
    rel = py_path.relative_to(ROOT)
    mod_name = str(rel.with_suffix("")).replace(os.sep, ".")
    module_doc, items, src = extract_module(py_path)
    
    if not module_doc and not items:
        return None

    # Calculer métriques pré-migration
    total_doc_lines = len(module_doc.split('\n')) if module_doc else 0
    total_doc_lines += sum(item['doc_lines'] for item in items)
    
    over_engineered_items = [item for item in items if item['is_over_engineered']]
    quantum_heavy = sum(item['quantum_terms'] for item in items) > 10
    
    # Créer documentation externe
    md_path = DOCS / (rel.with_suffix(".md").name)
    parts = [f"# {mod_name}\n"]
    
    # Header avec métriques
    parts.append(f"**Migré depuis**: `{rel}`  ")
    parts.append(f"**Lignes doc originales**: {total_doc_lines}  ")
    parts.append(f"**Éléments over-engineered**: {len(over_engineered_items)}  ")
    if quantum_heavy:
        parts.append("**⚛️ Module avec métaphores quantiques**  ")
    parts.append("\n---\n")
    
    # Documentation du module
    if module_doc.strip():
        parts += ["## Module Overview\n"]
        if len(module_doc.split('\n')) > MAX_DOCSTRING_LINES:
            parts.append("**(Documentation originale over-engineered - migrated from inline)**\n")
        parts += ["```text\n", md_escape(module_doc).rstrip(), "\n```\n"]
    
    # API Documentation
    if items:
        parts += ["## API Reference\n"]
        
        # Séparer over-engineered vs normal
        normal_items = [item for item in items if not item['is_over_engineered']]
        
        if over_engineered_items:
            parts += ["### 🚨 Over-engineered Components (migrated)\n"]
            for item in sorted(over_engineered_items, key=lambda x: x['doc_lines'], reverse=True):
                parts += [f"#### {item['name']} ({item['kind']})\n"]
                parts.append(f"**Original doc**: {item['doc_lines']} lines, {item['quantum_terms']} quantum terms\n\n")
                parts += ["```text\n", md_escape(item['doc']).rstrip(), "\n```\n"]
        
        if normal_items:
            parts += ["### Standard Components\n"]
            for item in sorted(normal_items, key=lambda x: x['name']):
                parts += [f"#### {item['name']} ({item['kind']})\n"]
                parts += ["```text\n", md_escape(item['doc']).rstrip(), "\n```\n"]
    
    # Écrire fichier markdown
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(parts), encoding="utf-8")

    # Générer stubs de remplacement
    stub_lines = []
    if module_doc.strip():
        if len(module_doc.split('\n')) > MAX_DOCSTRING_LINES:
            stub_lines.append(f'"""Over-engineered module docs → see: docs/api/{md_path.name}#module"""')
        else:
            stub_lines.append(f'"""Module docs → see: docs/api/{md_path.name}#module"""')
    
    for item in items:
        stub = create_stub_docstring(item['name'], f"docs/api/{md_path.name}", item['is_over_engineered'])
        stub_lines.append(f"# {item['name']}: {stub}")

    return {
        "py": str(rel),
        "md": str(md_path.relative_to(ROOT)),
        "stubs": stub_lines,
        "metrics": {
            "total_doc_lines": total_doc_lines,
            "over_engineered": len(over_engineered_items),
            "quantum_heavy": quantum_heavy
        }
    }

def main():
    """Migration principale avec rapport détaillé."""
    print("🧹 GREAT DOCUMENTATION MIGRATION - Starting...")
    print("=" * 60)
    
    report = []
    total_migrated_lines = 0
    total_over_engineered = 0
    
    # Scanner tous les fichiers Python
    for p in ROOT.rglob("*.py"):
        if any(part in str(p) for part in ["__pycache__", ".venv", "venv", "env", "build", ".git", "dist", "backup", ".mypy_cache", "kissbot-venv"]):
            continue
            
        res = migrate_file(p)
        if res:
            report.append(res)
            total_migrated_lines += res['metrics']['total_doc_lines']
            total_over_engineered += res['metrics']['over_engineered']

    # Créer INDEX
    index = ["# 📚 API Documentation Index\n"]
    index.append("*Generated by Great Documentation Migration Tool*\n")
    index.append(f"**Total docs migrated**: {len(report)} modules  ")
    index.append(f"**Lines migrated**: {total_migrated_lines:,}  ")
    index.append(f"**Over-engineered components**: {total_over_engineered}  ")
    index.append("\n---\n")
    
    # Index par catégorie
    quantum_modules = [r for r in report if r['metrics']['quantum_heavy']]
    normal_modules = [r for r in report if not r['metrics']['quantum_heavy']]
    
    if quantum_modules:
        index.append("## 🚨 Over-engineered Modules (Quantum Heavy)\n")
        for r in sorted(quantum_modules, key=lambda x: x['metrics']['total_doc_lines'], reverse=True):
            index.append(f"- `{r['py']}` → [{r['md']}]({r['md']}) ({r['metrics']['total_doc_lines']} lines)")
        index.append("\n")
    
    if normal_modules:
        index.append("## 📋 Standard Modules\n")
        for r in sorted(normal_modules, key=lambda x: x['py']):
            index.append(f"- `{r['py']}` → [{r['md']}]({r['md']})")
    
    (DOCS.parent / "INDEX.md").write_text("\n".join(index) + "\n", encoding="utf-8")

    # Rapport final
    print("\n🎯 MIGRATION REPORT")
    print("=" * 40)
    print(f"✅ Modules migrated: {len(report)}")
    print(f"📊 Total doc lines: {total_migrated_lines:,}")
    print(f"🚨 Over-engineered: {total_over_engineered}")
    print(f"📁 Documentation: docs/api/")
    print(f"📋 Index: docs/INDEX.md")
    
    print("\n🧹 TOP OFFENDERS:")
    worst = sorted(report, key=lambda x: x['metrics']['total_doc_lines'], reverse=True)[:5]
    for i, r in enumerate(worst, 1):
        print(f"{i}. {r['py']:40} {r['metrics']['total_doc_lines']:4} lines")
    
    print("\n💡 NEXT STEPS:")
    print("1. Review generated docs/api/ files")
    print("2. Replace docstrings in source with stubs")
    print("3. Run tests to ensure no breakage")
    print("4. Set up CI to prevent doc regrowth")
    
    print("\n🔗 STUB EXAMPLES (apply manually):")
    if report:
        sample = report[0]
        for stub in sample['stubs'][:3]:
            print(f"   {stub}")

if __name__ == "__main__":
    main()