import os
import json
import urllib.parse

def grammar_loader(filename):
    grammar = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            
            if not line or '::=' not in line:
                continue

            left_side , right_side = line.split('::=')
            key = left_side.strip()
            values = right_side.split('|')
            
            rules = []
            for value in values:
                tokens = value.strip().split()
                rules.append(tokens)

            rules.sort(key=len, reverse=True)

            grammar[key] = rules
            
    return grammar

def get_terminals(grammar):
    terminals = set()
    for rules in grammar.values():
        for rule in rules:
            for symbol in rule:
                if symbol not in grammar and symbol not in ['ε', 'epsilon']:
                    terminals.add(symbol)
    return terminals


def tokenize_word(sentence):
    if not sentence:
        return []
    return sentence.strip().split()

def tokenize_char(sentence):
    if not sentence:
        return []
    return [char for char in sentence if char.strip()]

def sentence_loader(filename, grammar=None):
    sentences = []
        
    is_char_level = False
    if grammar:
        terminals = get_terminals(grammar)
        if terminals and all(len(terminal) == 1 for terminal in terminals):
            is_char_level = True

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            
            if line.strip() == "" or line.strip() in ["ε", "epsilon"]:
                sentences.append([]) 
                continue
                
            if is_char_level:
                sentences.append(tokenize_char(line))
            else:
                sentences.append(tokenize_word(line))
                
    return sentences

def Parser(search_symbol, token_list, index, grammar, state):
    # NON-TERMINAL DURUMU
    if search_symbol in grammar:
        alternatives = grammar.get(search_symbol, [])
        
        for alternative in alternatives:
            current_index = index
            temp_results = []
            success = True
            
            for sub_symbol in alternative:
                result, next_index = Parser(sub_symbol, token_list, current_index, grammar, state)
                
                if result is None:
                    success = False
                    break
                
                temp_results.append((sub_symbol.strip('<>'), result))
                current_index = next_index
                
            if success:
                if len(temp_results) == 1 and not isinstance(temp_results[0][1], dict):
                    return temp_results[0][1], current_index
                
                sub_trees = {}
                for key, value in temp_results:
                    if key in sub_trees:
                        if isinstance(sub_trees[key], list):
                            sub_trees[key].append(value)
                        else:
                            sub_trees[key] = [sub_trees[key], value]
                    else:
                        sub_trees[key] = value
                return sub_trees, current_index
                
        return None, index

    # EPSILON DURUMU
    elif search_symbol in ['ε', 'epsilon']:
        return "ε", index

    # TERMINAL DURUMU
    else:
        if index < len(token_list) and token_list[index] == search_symbol:
            return search_symbol, index + 1
        else:
            if index > state["max_index"]:
                state["max_index"] = index
                state["expected_tokens"] = {search_symbol}
            elif index == state["max_index"]:
                state["expected_tokens"].add(search_symbol)
            return None, index

def check_sentence(start_symbol, tokens, grammar):
    state = {"max_index": 0, "expected_tokens": set()}
    tree, final_index = Parser(start_symbol, tokens, 0, grammar, state)

    if tree is not None and final_index == len(tokens):
        root_key = start_symbol.strip('<>')
        return True, {root_key: tree}, None

    #kısmi başarısız
    if tree is not None and final_index < len(tokens):
        if state["max_index"] <= final_index:
            error_details = {"index": final_index, "expected": set()}
        else:
            error_details = {"index": state["max_index"], "expected": state["expected_tokens"]}
        return False, None, error_details

    #tam başarısız
    error_details = {
        "index": state["max_index"],
        "expected": state["expected_tokens"]
    }
    return False, None, error_details

def get_token_category(token, grammar):
    for nonterminal, rules in grammar.items():
        for rule in rules:
            if token in rule:
                return nonterminal.strip('<>')
    return "unknown"

def format_error(tokens, error_details, grammar):
    index = error_details["index"]
    expected_set = error_details.get("expected", set())

    expected_list = sorted(list(expected_set))
    expected_string = " or ".join([f'"{expected}"' for expected in expected_list])

    expected_categories = set()
    for expected in expected_list:
        token_category = get_token_category(expected, grammar)
        if token_category != "unknown":
            expected_categories.add(token_category)
            
    expected_category_string = " or ".join(expected_categories) if expected_categories else "valid tokens"

    print("Error:")
    
    if len(tokens) == 0:
        print("Where the error occurs: at empty string")
        print(f"What was expected: a {expected_category_string} ({expected_string}) to start")
        print(f"Why the sentence is invalid: The sentence is empty, but grammar requires a {expected_category_string} to start")
        
    elif index >= len(tokens) and expected_set:
        print("Where the error occurs: at the end of the sentence")
        print(f"What was expected: a {expected_category_string} ({expected_string})")
        print(f"Why the sentence is invalid: The sentence ended prematurely. Expected a {expected_category_string} to complete the grammatical structure")
        
    elif index < len(tokens) and expected_set:
        error_token = tokens[index]
        invalid_token_category = get_token_category(error_token, grammar)

        print(f"Where the error occurs: at token {index + 1} {error_token}")
        
        if invalid_token_category == "unknown":
            print(f"What was expected: a {expected_category_string} ({expected_string})")
            print(f"Why the sentence is invalid: \"{error_token}\" is not defined in the vocabulary for {expected_category_string} in the grammar.")
        
        else:
            if index == 0:
                print(f"What was expected: a {expected_category_string} ({expected_string}) to start")
                print(f"Why the sentence is invalid: the sentence begins with a {invalid_token_category}, but grammar requires a {expected_category_string} at the beginning")
            else:
                print(f"What was expected: a {expected_category_string} ({expected_string})")
                print(f"Why the sentence is invalid: found a {invalid_token_category}, but grammar structurally requires a {expected_category_string} here")

    elif index < len(tokens) and not expected_set:
        error_token = tokens[index]
        print(f"Where the error occurs: at token {index + 1} {error_token}")
        print("What was expected: End of sentence (No more tokens expected)")
        print(f"Why the sentence is invalid: The grammatical structure was already valid and complete, but an extra token {error_token} was found.")


def build_parse_tree_dot(parse_tree):
    dot_lines = ["digraph ParseTree {", "  node [shape=ellipse];"]
    node_id_counter = [0]

    def add_node(node_label, shape="ellipse", style=""):
        node_id = f"n{node_id_counter[0]}"
        node_id_counter[0] += 1

        render_label = "ε" if node_label == "epsilon" else str(node_label)
        escaped_label = render_label.replace('"', '\\"')

        dot_lines.append(
            f'  {node_id} [label="{escaped_label}", shape={shape}{style}];'
        )
        return node_id

    def traverse(node_key, subtree, parent_node_id):
        display_node_label = "ε" if node_key == "epsilon" else f"<{node_key}>"
        current_node_id = add_node(display_node_label)

        if parent_node_id:
            dot_lines.append(f'  {parent_node_id} -> {current_node_id};')

        if isinstance(subtree, dict):
            for child_key, child_value in subtree.items():
                traverse(child_key, child_value, current_node_id)

        elif isinstance(subtree, list):
            for item in subtree:
                if isinstance(item, dict):
                    for child_key, child_value in item.items():
                        traverse(child_key, child_value, current_node_id)

                elif isinstance(item, str):
                    terminal_node_id = add_node(
                        item,
                        shape="box",
                        style=", style=filled, fillcolor=lightblue"
                    )
                    dot_lines.append(f'  {current_node_id} -> {terminal_node_id};')

        elif isinstance(subtree, str):
            terminal_node_id = add_node(
                subtree,
                shape="box",
                style=", style=filled, fillcolor=lightblue"
            )
            dot_lines.append(f'  {current_node_id} -> {terminal_node_id};')

    if isinstance(parse_tree, dict):
        for root_key, root_value in parse_tree.items():
            traverse(root_key, root_value, None)

    dot_lines.append("}")
    return "\n".join(dot_lines)

if __name__ == "__main__":

    grammar_file = "grammar1.txt" 
    sentences_file = "sentences1.txt"

    if not os.path.exists(grammar_file):
        print(f"Error: {grammar_file} not found")
        grammar = {}
    else:
        grammar = grammar_loader(grammar_file)
        
    sentences = sentence_loader(sentences_file, grammar)
    os.system('cls' if os.name == 'nt' else 'clear')

    print(f"Example {grammar_file}: ")
    try:
        with open(grammar_file, 'r', encoding='utf-8') as file:
            print(file.read().strip())
    except FileNotFoundError: pass

    print("\n") 
    print(f"Example {sentences_file}: ")
    try:
        with open(sentences_file, 'r', encoding='utf-8') as file:
            print(file.read())
    except FileNotFoundError: pass
        
    print("\n-----------------------------------------------------------------------------------------------------------------------------------------\n")
 
    if grammar and sentences is not None:
        start_symbol = list(grammar.keys())[0]

        for tokens in sentences:
            sentence_string = " ".join(tokens) if tokens else "ε"
            print(f"Input: {sentence_string}")
            
            is_valid, tree, error_details = check_sentence(start_symbol, tokens, grammar)

            if is_valid:
                print("\033[92mValid\033[0m")
                
                dot_code = build_parse_tree_dot(tree)
                base_url = "https://quickchart.io/graphviz?graph="
                long_url = base_url + urllib.parse.quote(dot_code)
                
                print("\nParse Tree:")
                clickable_text = "Please click to see the tree"
                osc8_link = f"\033]8;;{long_url}\a\033[94m{clickable_text}\033[0m\033]8;;\a"
                print(osc8_link)

                print("\nJSON:")
                print(json.dumps(tree, indent=4, ensure_ascii=False))
            else:
                print("\033[91mInvalid\033[0m")
                format_error(tokens, error_details, grammar)
            print("\n-----------------------------------------------------------------------------------------------------------------------------------------\n")