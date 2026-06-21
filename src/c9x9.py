# c9x9.py: 九九乘法表生成器

def generate_9x9_multiplication_table():
    """
    Generates and prints the complete 99 multiplication table.
    Each line displays an equation in the format "a × b = result", covering all combinations from a=1 to 9, b=1 to 9.
    Follows PEP8 style guidelines for readability and consistency.
    """
    # Use nested loops to iterate through numbers 1-9
    # For each combination (i, j), calculate the product i * j
    # Print or return formatted strings with tab separation for alignment

    for a in range(1, 10):  # Iterate from 1 to 9 for 'a'
        line = ""
        for b in range(1, 10):  # Iterate from 1 to 9 for 'b'
            result = a * b
            if b > 1:
                line += "\t"  # Add tab separation after the first element on each row
            equation = f"{a} × {b} = {result}"
            line += equation
        
        print(line)  # Print each formatted line directly

# Optional: If this file is meant to be executed as a script, include a main function
if __name__ == "__main__":
    import sys
    
    # Check for command-line arguments if needed (not specified by user)
    if len(sys.argv) > 1:
        print("Usage: python c9x9.py [optional parameters] - not implemented yet.")
    
    # Generate and display the table immediately when run
    generate_9x9_multiplication_table()