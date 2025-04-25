from rich.console import Console
from rich.align import Align
from rich.panel import Panel

console = Console()
term_width = console.size.width

# Example LLM output
llm_output = """
The ancient ruins whisper tales of forgotten times.
Moss-covered stones bear the weight of legends untold.
A faint glow pulses from within the obsidian altar...
""".strip()

# Clear screen
console.clear()

# Center the output panel
centered_output = Align(Panel(llm_output, expand=False), align="center", vertical="middle")
console.print(centered_output, height=20)

# --- Centered but slightly left-shifted input prompt ---
shift = 10  # Shift input this many spaces to the left from full center
prompt_width = len(">")
input_prompt_x = max((term_width - prompt_width) // 2 - shift, 0)

# Print the prompt and read input
console.print("\n" + " " * input_prompt_x + "[bold cyan]> [/bold cyan]", end="")
user_input = input()

while (user_input != 'quit'):
    console.print(centered_output, height=20)

# --- Centered but slightly left-shifted input prompt ---
    shift = 10  # Shift input this many spaces to the left from full center
    prompt_width = len(">")
    input_prompt_x = max((term_width - prompt_width) // 2 - shift, 0)

# Print the prompt and read input
    console.print("\n" + " " * input_prompt_x + "[bold cyan]> [/bold cyan]", end="")
    user_input = input()


