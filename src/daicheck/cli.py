import sys

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
CYAN = "\033[36m"
GRAY = "\033[90m"

PROGRAM = "daicheck"

REQUIRED_FIELDS = {
    "Arch",
    "Other_names",
    "Dovian_Runs",
    "Dovian_Embedded_Runs",
    "More",
    "Release",
}

def fail(message):
    print(f"{RED}{PROGRAM}: error:{RESET} {message}")
    sys.exit(1)

def parse_file(path):
    data = {}

    try:
        with open(path, "r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, 1):
                line = raw_line.strip()

                if not line:
                    continue

                if ":" not in line:
                    fail(f"line {line_number}: invalid syntax")

                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if not key or not value:
                    fail(f"line {line_number}: invalid field")

                if key in data:
                    fail(f"line {line_number}: duplicate field '{key}'")

                data[key] = value

    except FileNotFoundError:
        fail(f"file not found: {path}")
    except OSError as error:
        fail(f"cannot read '{path}': {error}")

    missing = REQUIRED_FIELDS - data.keys()

    if missing:
        fail(f"missing field(s): {', '.join(sorted(missing))}")

    return data

def validate(data):
    for field in ("Dovian_Runs", "Dovian_Embedded_Runs"):
        if data[field] not in ("Yes", "No"):
            fail(f"{field} must be 'Yes' or 'No'")

    try:
        release = int(data["Release"])
    except ValueError:
        fail("Release must be a valid year")

    if release < 1900 or release > 2100:
        fail("Release must be between 1900 and 2100")

def compatibility(value):
    if value == "Yes":
        return f"{GREEN}supported{RESET}"
    return f"{RED}not supported{RESET}"

def show_info(data):
    aliases = ", ".join(data["Other_names"].split())

    print()
    print(f"{CYAN}{BOLD}DAI INFO{RESET}")
    print(f"{GRAY}────────{RESET}")
    print(f"Architecture           : {data['Arch']}")
    print(f"Aliases                : {aliases}")
    print(f"Dovian                 : {compatibility(data['Dovian_Runs'])}")
    print(f"Dovian Embedded        : {compatibility(data['Dovian_Embedded_Runs'])}")
    print(f"Release                : {data['Release']}")
    print(f"More                   : {data['More']}")
    print()
    print(f"Status                 : {GREEN}{BOLD}VALID ✓{RESET}")

def main():
    args = sys.argv[1:]
    show = False
    file = None

    for arg in args:
        if arg == "-i":
            show = True
        elif arg.startswith("-"):
            fail(f"unknown option '{arg}'")
        elif file is None:
            file = arg
        else:
            fail("multiple input files are not supported")

    if file is None:
        fail("no input file specified")

    if not file.endswith(".dai"):
        fail("input file must have a .dai extension")

    data = parse_file(file)
    validate(data)

    if show:
        show_info(data)
    else:
        print(f"{GREEN}{PROGRAM}: {file}: valid ✓{RESET}")

if __name__ == "__main__":
    main()
