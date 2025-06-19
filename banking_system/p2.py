def parse_grammar(rules):
    """
    Converts grammar rules into a dictionary.
    """
    grammar = {}
    for rule in rules:
        lhs, rhs = rule.split("->")
        lhs = lhs.strip()
        productions = rhs.strip().split("|")
        for production in productions:
            production = production.strip()
            if production not in grammar:
                grammar[production] = []
            grammar[production].append(lhs)
    return grammar

def initialize_table(input_string, grammar):
    """
    Initializes the DP table for terminals.
    """
    n = len(input_string)
    dp_table = [[[] for _ in range(n)] for _ in range(n)]
    for i in range(n):
        token = input_string[i]
        if token in grammar:
            dp_table[i][i] = grammar[token]
    return dp_table

def fill_table(dp_table, grammar, n):
    """
    Populates the DP table using the CYK algorithm.
    """
    for length in range(2, n + 1):  # Substring lengths
        for i in range(n - length + 1):  # Start index
            j = i + length - 1  # End index
            for k in range(i, j):  # Split point
                for B in dp_table[i][k]:
                    for C in dp_table[k + 1][j]:
                        rule = B + " " + C
                        if rule in grammar:
                            dp_table[i][j].extend(grammar[rule])
    # Remove duplicates and sort
    for i in range(n):
        for j in range(n):
            dp_table[i][j] = sorted(set(dp_table[i][j]))

def format_table(dp_table, n):
    """
    Formats the DP table with the specified output style.
    """
    formatted_table = []
    for i in range(n):
        formatted_row = []
        for j in range(n):
            if j < i:  # Lower triangle (untouched cells)
                formatted_row.append(";")
            elif not dp_table[i][j]:  # Empty cells in the upper triangle
                formatted_row.append("-;")
            else:  # Non-empty cells
                formatted_row.append(", ".join(dp_table[i][j]))
        formatted_table.append(" ".join(formatted_row))
    return "\n".join(formatted_table)

def cyk_algorithm(grammar_rules, input_string):
    """
    Runs the CYK algorithm and returns the results.
    """
    grammar = parse_grammar(grammar_rules)
    n = len(input_string)
    dp_table = initialize_table(input_string, grammar)
    fill_table(dp_table, grammar, n)
    formatted_table = format_table(dp_table, n)

    is_accepted = 1 if "Sent" in dp_table[0][n - 1] else 0
    return is_accepted, formatted_table

# Main program to handle file inputs and outputs
def main():
    # Read grammar rules from 'grammar.txt'
    with open('grammar.txt', 'r') as grammar_file:
        grammar_rules = [line.strip() for line in grammar_file.readlines()]

    # Read input string from 'input.txt'
    with open('input.txt', 'r') as input_file:
        input_string = input_file.readline().strip().split()

    # Run the CYK Algorithm
    is_accepted, dp_table = cyk_algorithm(grammar_rules, input_string)

    # Write the results to 'output.txt'
    with open('output.txt', 'w') as output_file:
        output_file.write(f"{is_accepted}\n")
        output_file.write(dp_table)

# Run the main function
if __name__ == "__main__":
    main()
