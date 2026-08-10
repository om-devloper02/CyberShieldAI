import os
import sys

# Fix all __init__.py files
init_files = [
    'scanner/__init__.py',
    'scanner/website/__init__.py',
    'scanner/email/__init__.py',
    'scanner/malware/__init__.py',
    'scanner/network/__init__.py',
    'ai/__init__.py',
    'ai/classifiers/__init__.py',
    'utils/__init__.py',
    'models/__init__.py',
    'routes/__init__.py',
    'tests/__init__.py',
]

print("Fixing __init__.py files...")
for fpath in init_files:
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write('# package\n')
    with open(fpath, 'rb') as f:
        data = f.read()
    nulls = data.count(b'\x00')
    status = 'OK' if nulls == 0 else f'STILL HAS {nulls} NULLS!'
    print(f"  {fpath}: {len(data)} bytes [{status}]")

print("\nVerifying imports...")
import importlib.util

def test_import(module_path, file_path):
    spec = importlib.util.spec_from_file_location(module_path, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print(f"  OK: {module_path}")

test_import('scanner.website.analyzer', 'scanner/website/analyzer.py')
test_import('scanner.email.analyzer', 'scanner/email/analyzer.py')
test_import('scanner.malware.analyzer', 'scanner/malware/analyzer.py')
test_import('scanner.network.scanner', 'scanner/network/scanner.py')
test_import('scanner.password_analyzer', 'scanner/password_analyzer.py')
test_import('ai.classifiers.classifier', 'ai/classifiers/classifier.py')

print("\nAll checks passed! Ready to start.")
