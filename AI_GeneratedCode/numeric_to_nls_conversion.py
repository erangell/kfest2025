def convert_to_nls_format(dotted_numeric):
    """
    Convert a dotted numeric string to NLS alternating alphanumeric format.
    
    In NLS format:
    - Even-positioned levels (0-indexed) use numeric characters
    - Odd-positioned levels use alphabetic characters
    - For alphabetic levels with values > 26, use double letters (aa, ab, ...)
    
    Example:
    1.27.28.29 -> 1aa28ab
    
    Args:
        dotted_numeric (str): A dotted numeric string like "1.2.3.4"
        
    Returns:
        str: The NLS alternating alphanumeric representation without periods
    """
    if not dotted_numeric:
        return ""
    
    parts = dotted_numeric.split('.')
    result = []
    
    for i, part in enumerate(parts):
        # Convert to integer
        num = int(part)
        
        # Even positions (0, 2, 4...) remain numeric
        if i % 2 == 0:
            result.append(str(num))
        # Odd positions (1, 3, 5...) convert to alphabetic
        else:
            result.append(convert_to_alpha(num))
    
    return ''.join(result)

def convert_to_alpha(num):
    """
    Convert a numeric value to alphabetic NLS format.
    
    Args:
        num (int): A positive integer
        
    Returns:
        str: Alphabetic representation (a-z, then aa, ab, etc.)
    """
    if num <= 0:
        raise ValueError("Input must be a positive integer")
    
    # Adjust num to be 0-indexed
    num -= 1
    
    # For values 1-26, return lowercase letters a-z
    if num < 26:
        return chr(97 + num)  # 97 is ASCII for 'a'
    
    # For values > 26, use multiple letters
    quotient, remainder = divmod(num, 26)
    first_letter = chr(97 + quotient - 1)
    second_letter = chr(97 + remainder)
    
    return first_letter + second_letter

# Test examples
test_cases = [
    "1.2.3.4",
    "1.27.28.29",
    "5.6.7.8.9.10",
    "1.52.3.4",
    "10.26.30.55"
]

for test in test_cases:
    print(f"{test} -> {convert_to_nls_format(test)}")
