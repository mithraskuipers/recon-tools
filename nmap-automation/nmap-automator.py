import subprocess
import questionary
from questionary import Choice
from typing import Dict, Set, List
import os


# Unique identifiers for scan options
SCAN_OPTION_IDS = {
    "full_port_scan": "Full port scan",
    "top_1000_ports_scan": "1000 most used ports scan",
    "ping_scan": "Ping scan",
    "tcp_scan": "TCP scan",
    "udp_scan": "UDP scan",
    "os_detection": "OS detection",
    "version_detection": "Version detection",
    "version_intensity": "Version intensity"
}

# Configuration for scan options
SCAN_OPTIONS = {
    SCAN_OPTION_IDS["full_port_scan"]: {
        "command": "-p-",
        "conflicts": {SCAN_OPTION_IDS["top_1000_ports_scan"], SCAN_OPTION_IDS["ping_scan"]},
        "description": "Scan all 65535 ports"
    },
    SCAN_OPTION_IDS["top_1000_ports_scan"]: {
        "command": "",
        "conflicts": {SCAN_OPTION_IDS["full_port_scan"], SCAN_OPTION_IDS["ping_scan"]},
        "description": "Default Nmap scan of top ports"
    },
    SCAN_OPTION_IDS["ping_scan"]: {
        "command": "-sn",
        "conflicts": {SCAN_OPTION_IDS["full_port_scan"], SCAN_OPTION_IDS["top_1000_ports_scan"], SCAN_OPTION_IDS["tcp_scan"], SCAN_OPTION_IDS["udp_scan"]},
        "description": "Only check if hosts are online"
    },
    SCAN_OPTION_IDS["tcp_scan"]: {
        "command": "-sT",
        "conflicts": {SCAN_OPTION_IDS["ping_scan"]},
        "description": "TCP connect scan"
    },
    SCAN_OPTION_IDS["udp_scan"]: {
        "command": "-sU",
        "conflicts": {SCAN_OPTION_IDS["ping_scan"]},
        "description": "UDP port scan"
    },
    SCAN_OPTION_IDS["os_detection"]: {
        "command": "--osscan-guess",
        "conflicts": set(),
        "description": "Enable OS detection"
    },
    SCAN_OPTION_IDS["version_detection"]: {
        "command": "-sV",
        "conflicts": set(),
        "description": "Detect service versions"
    },
    SCAN_OPTION_IDS["version_intensity"]: {
        "command": "--version-intensity",
        "conflicts": set(),
        "description": "Set version detection intensity",
        "requires_input": True,
        "input_prompt": "Enter the version intensity level (0-9):",
        "input_validator": lambda x: x.isdigit() and 0 <= int(x) <= 9
    }
}

# Menu options and their corresponding functions
MENU_OPTIONS = {
    "Automated Scan": "automated_scan",
    "Manual Scan": "manual_scan",  # Easy to add new menu options here
    "Exit": "exit_program"
}



def clear_screen():
    """Clear the terminal screen (Linux/Unix)"""
    os.system("clear")  # or os.system("cls") for Windows

def select_scan_options(selected_options: Set[str], current_position: int, is_first_time: bool) -> tuple[Set[str], int]:
    """Handle the selection of scan options."""
    choices = []
    for option in SCAN_OPTIONS.keys():
        prefix = "*" if option in selected_options else " "
        choices.append(Choice(f"{prefix} {SCAN_OPTIONS[option]['description']}", option))
    choices.append(Choice("Done", "Done"))
    clear_screen()
    
    # Now we make the selection call without a prompt text, so no prompt appears after the first time
    choice = questionary.select(
        "",
        choices=choices,
        default=choices[current_position].value
    ).ask()

    if choice == "Done":
        return selected_options, -1

    current_position = [c.value for c in choices].index(choice)

    # Toggle the selected option
    if choice in selected_options:
        selected_options.remove(choice)
    else:
        # Handle conflicts before adding new option
        for conflict in SCAN_OPTIONS[choice]["conflicts"]:
            if conflict in selected_options:
                selected_options.remove(conflict)
        selected_options.add(choice)

    # Ensure current_position stays within bounds
    if current_position >= len(choices) - 1:
        current_position = len(choices) - 2

    return selected_options, current_position




def build_nmap_command(selected_options: Set[str], target_ip: str) -> List[str]:
    """Build the Nmap command based on selected options."""
    command = ["nmap"]

    for option in selected_options:
        if SCAN_OPTIONS[option]["command"]:
            command.append(SCAN_OPTIONS[option]["command"])
            
            # Handle options that require additional input
            if SCAN_OPTIONS[option].get("requires_input"):
                while True:
                    value = questionary.text(SCAN_OPTIONS[option]["input_prompt"]).ask()
                    if SCAN_OPTIONS[option]["input_validator"](value):
                        command.append(value)
                        break
                    print("Invalid input. Please try again.")

    command.append(target_ip)
    return command

def execute_nmap_command(command: List[str]) -> None:
    """Execute the Nmap command and handle errors."""
    print("\nGenerated Nmap command:")
    print(" ".join(command))

    if questionary.confirm("Do you want to execute this command?").ask():
        try:
            subprocess.run(command)
        except FileNotFoundError:
            print("Error: Nmap is not installed or not found in your system's PATH.")

def automated_scan() -> None:
    """Handle automated scan workflow."""
    clear_screen()
    target_ip = "192.168.2.100"  # You can make this configurable if needed
    selected_options = set()
    current_position = 0
    is_first_time = True  # Track if it's the first time selecting options

    while True:
        selected_options, current_position = select_scan_options(selected_options, current_position, is_first_time)
        if current_position == -1:  # User selected "Done"
            break
        is_first_time = False  # After the first time, we stop printing the prompt again

    command = build_nmap_command(selected_options, target_ip)
    execute_nmap_command(command)

    print("\nScan completed. Exiting program.")
    exit()

def manual_scan() -> None:
    """Handle manual scan workflow."""
    # Add your manual scan implementation here
    print("Manual scan feature coming soon...")
    exit()

def exit_program() -> None:
    """Handle program exit."""
    print("Exiting...")
    exit()

def main() -> None:
    """Main program loop."""
    clear_screen()
    # Map menu options to functions
    function_map = {
        "Automated Scan": automated_scan,
        "Manual Scan": manual_scan,
        "Exit": exit_program
    }

    while True:
        choice = questionary.select(
            "What do you want to do with Nmap?",
            choices=list(MENU_OPTIONS.keys())
        ).ask()

        # Execute the selected function and stop if it ends
        function_map[choice]()
        break  # This will exit the program after executing the selected choice.

if __name__ == "__main__":
    main()

