import os
import glob
import python_minifier
from tqdm import tqdm
from post_obfuscate import *

# Configuration
apply_advanced_obfuscation = True
integration_path = 'tis_integration_original'
output_path = 'tis_integration'

files_not_to_obfuscate = [
    'const.py',
    'tis_configuration_dashboard.py',
]

# Create output directory if it doesn't exist
os.makedirs(output_path, exist_ok=True)

# Process Python files
for file_path in tqdm(glob.glob(os.path.join(integration_path, '**', '*.py'), recursive=True)):
    rel_path = os.path.relpath(file_path, integration_path)
    output_file = os.path.join(output_path, rel_path)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Read source
    with open(file_path, 'r') as f:
        source = f.read()

    # Apply minification with appropriate options
    minified = python_minifier.minify(
        source,
        remove_literal_statements=True,
        combine_imports=True,
    )

    # Replace tabs with spaces
    minified = minified.replace('\t', '    ')  # Replace tabs with 4 spaces

    # Apply advanced obfuscation
    minified = advanced_obfuscate(minified) if apply_advanced_obfuscation else minified

    # Save minified source
    with open(output_file, 'w') as f:
        f.write(minified if os.path.basename(file_path) not in files_not_to_obfuscate else source)

# Copy non-Python files
for file_path in tqdm(glob.glob(os.path.join(integration_path, '**', '*.*'), recursive=True)):
    if not file_path.endswith('.py'):
        rel_path = os.path.relpath(file_path, integration_path)
        output_file = os.path.join(output_path, rel_path)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Copy file
        with open(file_path, 'rb') as src, open(output_file, 'wb') as dst:
            dst.write(src.read())

print(f"Obfuscation complete. Files saved to {output_path}")
