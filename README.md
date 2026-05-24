# Mini Language Parser and Parse Tree Generator

## Overview
This project is a syntactic analyzer designed to evaluate the structural validity of input sentences based on dynamically loaded Context-Free Grammar (CFG) rules. Built with Python, it employs a **top-down, recursive descent parsing algorithm** with a robust backtracking mechanism to explore derivation paths and verify grammar compliance.

## Features
* **Dynamic Grammar Loading:** Reads BNF-style production rules directly from external text files, allowing the parser to adapt to various languages.
* **Flexible Tokenization:** Automatically categorizes terminals and applies either word-level or character-level tokenization based on the grammar structure.
* **Epsilon (ε) Transitions:** Seamlessly handles empty strings and epsilon transitions within grammar rules.
* **Visual Parse Trees:** For valid syntax, the system generates a hierarchical JSON representation and provides an automated visual parse tree link via the QuickChart/Graphviz API.
* **Advanced Error Detection:** Implements a "reach-back" error reporting mechanism. If parsing fails, it pinpoints the exact token index where the error occurred, identifies the unexpected token, and lists the expected symbol categories to help with debugging.

## File Structure
* project.py: The main script containing the recursive descent parser, tokenizer, and error-handling logic.
* grammar1.txt / grammar2.txt: Example files containing the CFG rules.
* sentences1.txt / sentences2.txt: Example test inputs (valid and invalid sentences).
* report.pdf: Detailed project documentation, methodology, mathematical models, and test results.


## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/belkizozmus/Mini-Language-Parser-Project.git

2. Navigate to the project directory and run the main script:
   ```bash
   python project.py

3. The script will process the test sentences against the loaded grammar.
4. **For valid sentences:** Click the generated QuickChart link in the terminal to view the visual parse tree.
5. **For invalid sentences:** Review the detailed console report to see why the syntactic validation failed.

## Example Output

**Valid Sentence:**

```text
Input: a telescope admired the cat
Valid

Parse Tree:
Please click to see the tree (Link provided in terminal)

JSON:
{
    "sentence": {
        "noun-phrase": {
            "determiner": "a",
            "noun": "telescope"
        },
        "verb-phrase": {
            "verb": "admired",
            "noun-phrase": {
                "determiner": "the",
                "noun": "cat"
            }
        }
    }
}

```

**Invalid Sentence:**

```text
Input: liked the dog
Invalid

Error:
Where the error occurs: at token 1 liked
What was expected: a determiner ("a" or "the") to start
Why the sentence is invalid: the sentence begins with a verb, but grammar requires a determiner at the beginning

