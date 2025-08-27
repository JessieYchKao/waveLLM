import sys

def vcd_to_text(input_vcd, output_txt):
    try:
        with open(input_vcd, 'r') as vcd_file, open(output_txt, 'w') as output_file:
            signals = {}  # Mapping from identifier codes to signal info
            scopes = []   # Stack to keep track of scopes (module hierarchy)
            timescale = ''
            parsing_header = True

            output_file.write("== VCD Signals and Hierarchy ==\n")

            for line in vcd_file:
                line = line.strip()
                if parsing_header:
                    if line.startswith('$timescale'):
                        # Extract timescale
                        timescale_line = line
                        while not line.endswith('$end'):
                            line = next(vcd_file).strip()
                            timescale_line += ' ' + line
                        timescale = timescale_line.replace('$timescale', '').replace('$end', '').strip()
                        output_file.write(f"Timescale: {timescale}\n")
                    elif line.startswith('$scope'):
                        # Entering a new scope
                        tokens = line.split()
                        scope_type = tokens[1]
                        scope_name = tokens[2]
                        scopes.append(scope_name)
                    elif line.startswith('$upscope'):
                        # Exiting a scope
                        scopes.pop()
                    elif line.startswith('$var'):
                        # Variable definition
                        tokens = line.split()
                        var_type = tokens[1]
                        var_size = tokens[2]
                        identifier_code = tokens[3]
                        var_name = tokens[4]
                        full_name = '.'.join(scopes + [var_name])
                        signals[identifier_code] = {
                            'name': full_name,
                            'size': var_size,
                            'type': var_type
                        }
                        output_file.write(f"Signal: {full_name} (Size: {var_size} bits)\n")
                    elif line.startswith('$enddefinitions'):
                        parsing_header = False
                        output_file.write("\n== Value Changes ==\n")
                else:
                    # Parsing value changes
                    if line.startswith('#'):
                        # Timestamp
                        timestamp = int(line[1:])
                        output_file.write(f"\nTime: {timestamp}\n")
                    elif line == '':
                        continue  # Skip empty lines
                    else:
                        # Value change
                        if line.startswith('b') or line.startswith('r'):
                            # Vector value change
                            tokens = line.split()
                            value = tokens[0][1:]  # Remove 'b' or 'r'
                            identifier_code = tokens[1]
                        else:
                            # Scalar value change
                            value = line[0]
                            identifier_code = line[1:]
                        if identifier_code in signals:
                            signal_name = signals[identifier_code]['name']
                            output_file.write(f"{signal_name}: {value}\n")
                        else:
                            output_file.write(f"Unknown signal {identifier_code}: {value}\n")

            print(f"Conversion complete. Output written to {output_txt}")

    except Exception as e:
        print(f"Error processing VCD file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python vcd_to_text.py <input.vcd> <output.txt>")
        sys.exit(1)
    input_vcd = sys.argv[1]
    output_txt = sys.argv[2]
    vcd_to_text(input_vcd, output_txt)