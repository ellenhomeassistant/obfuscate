import base64
import re
import random
import string

def process_line(line):
    # Generate a unique marker for this line
    marker = ''.join(random.choice(string.ascii_letters) for _ in range(16))
    processed_sections = {}

    # Helper function to process a string match
    def process_string_match(match, is_f_string=False):
        entire_match = match.group(0)
        if entire_match in processed_sections:
            return None

        # For f-strings, we need special handling
        if is_f_string:
            template = match.group(1)
            var_parts = re.findall(r'\{([^}]+)\}', template)

            formatted_template = template
            for i, var in enumerate(var_parts):
                formatted_template = formatted_template.replace(f'{{{var}}}', f'{{__var{i}}}')

            vars_str = ', '.join([f'__var{i}={var}' for i, var in enumerate(var_parts)])
            encoded_template = base64.b64encode(formatted_template.encode()).decode()
            replacement = f'beta__("{encoded_template}", {vars_str})'
        else:
            # For normal strings, just encode the content
            content = match.group(1)
            encoded = base64.b64encode(content.encode()).decode()
            replacement = f'alpha__("{encoded}")'

        key = f"{marker}{len(processed_sections)}"
        processed_sections[key] = replacement
        return key

    # Process each pattern type
    patterns = [
        (r'f"([^"\\]*(\\.[^"\\]*)*)"', True),     # f-strings with double quotes
        (r"f'([^'\\]*(\\.[^'\\]*)*)'", True),     # f-strings with single quotes
        (r'(?<![rfbu\w])"([^"\\]*(\\.[^"\\]*)*)"', False),  # normal strings with double quotes
        (r"(?<![rfbu\w])'([^'\\]*(\\.[^'\\]*)*)'", False)   # normal strings with single quotes
    ]

    current_line = line
    for pattern, is_f_string in patterns:
        matches = list(re.finditer(pattern, current_line))
        for match in reversed(matches):
            key = process_string_match(match, is_f_string)
            if key:
                current_line = current_line[:match.start()] + key + current_line[match.end():]

    # Replace all markers with their processed versions
    for key, replacement in processed_sections.items():
        current_line = current_line.replace(key, replacement)

    return current_line

def advanced_obfuscate(input_code):
    # Remove the 'from __future__ import annotations' statement from the input code
    code = re.sub(r'from __future__ import annotations\s*', '', input_code)

    # Remove doc strings
    code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
    code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)

    # Add a space after every return statement
    code = re.sub(r'return(\S)', r'return \1', code)

    # Process each line independently
    lines = code.split('\n')
    processed_lines = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            processed_lines.append(line)
            continue
            
        # Process non-empty lines
        processed_line = process_line(line)
        processed_lines.append(processed_line)

    # Add decoder functions
    decoder = """from __future__ import annotations
from TISControlProtocol import *
"""
    
    # Join all processed lines
    final_code = '\n'.join(processed_lines)
    return decoder + final_code