
from pathlib import Path
import re




def clean_vtt_to_script(vtt_file_path):
    """
    Converts a VTT (WebVTT subtitle) file to a cleaned script text.
    Reads the specified VTT file, removes timestamps, numbering, empty lines, 
    and duplicate lines caused by overlapping captions. Combines the 
    remaining lines into a single string, removes extra spaces before punctuation, and strips out any HTML tags.

    Args:
        vtt_file_path (str or Path): The path to the VTT file to be processed.
    Returns:
        str: The cleaned script text extracted from the VTT file.
    """
    lines = Path(vtt_file_path).read_text(encoding='utf-8').splitlines()
    cleaned_lines = []
    previous_line = ""

    for line in lines:
        line = line.strip()

        # Skip empty lines, timestamps, and numbering
        if not line or '-->' in line or re.match(r'^\d+$', line):
            continue

        # Avoid duplications due to overlapping captions
        if line == previous_line:
            continue

        # Append if not redundant
        cleaned_lines.append(line)
        previous_line = line

    # Combine lines and fix common subtitle formatting
    text = " ".join(cleaned_lines)

    # Optional cleanup: Remove extra spaces before punctuation
    text = re.sub(r'\s+([.,?!])', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)

    return text
