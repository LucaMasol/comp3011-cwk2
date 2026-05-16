from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Callable

PROMPT = "> "

@dataclass(frozen=True)
class ParsedCommand:
  """A command given in the shell"""
  name: str
  args: list[str]


def parse_command(raw_input: str) -> ParsedCommand | None:
  """Convert a shell input into a command"""
  stripped_input = raw_input.strip()

  if not stripped_input:
    return None

  try:
    parts = shlex.split(stripped_input)
  except ValueError as error:
    print(f"Error: could not parse command: {error}")
    return None

  command_name = parts[0].lower()
  command_args = parts[1:]

  return ParsedCommand(name=command_name, args=command_args)


def handle_build(args: list[str]) -> None:
  if args and args != ["-v"]:
    print("Usage: build [-v]")
    return

  pass


def handle_load(args: list[str]) -> None:
  if args:
    print("Usage: load")
    return

  pass


def handle_print(args: list[str]) -> None:
  if len(args) != 1:
    print("Usage: print <word>")
    return

  word = args[0]
  pass


def handle_find(args: list[str]) -> None:
  if not args:
    print("Usage: find <string>")
    return

  query = " ".join(args)
  pass


def print_help() -> None:
  print("Available commands:")
  print("  build                  #  Build and store inverted index to ./data/index.json")
  print("  load                   #  Load inverted index from ./data/index.json")
  print("  print <word>           #  Print the index entry for a word")
  print("  find <word> [word ...] #  Find pages matching a string")
  print("  help                   #  Show commands and their usage")
  print("  exit | quit            #  Exit shell")


CommandHandler = Callable[[list[str]], None]

COMMAND_HANDLERS: dict[str, CommandHandler] = {
  "build": handle_build,
  "load": handle_load,
  "print": handle_print,
  "find": handle_find,
}


def execute_command(parsed_command: ParsedCommand) -> bool:
  """Run a parsed command. Returns False to exit shell."""
  command_name = parsed_command.name
  command_args = parsed_command.args

  if command_name in {"exit", "quit"}:
    if command_args:
      print(f"Usage: {command_name}")
      return True
    return False

  if command_name == "help":
    if command_args:
      print(f"Usage: {command_name}")
      return True

    print_help()
    return True

  handler = COMMAND_HANDLERS.get(command_name)

  if handler is None:
    print(f"Unknown command: {command_name}")
    print("Run 'help' to see available commands.")
    return True

  handler(command_args)
  return True


def run_shell() -> None:
  """Run the shell"""
  print("Search tool shell. Type 'help' for commands or 'exit' to quit.")

  while True:
    try:
      raw_input = input(PROMPT)
    except EOFError:
      print()
      break

    parsed_command = parse_command(raw_input)

    if parsed_command is None:
      continue

    should_continue = execute_command(parsed_command)

    if not should_continue:
      break


def main() -> None:
  run_shell()
if __name__ == "__main__":
  main()