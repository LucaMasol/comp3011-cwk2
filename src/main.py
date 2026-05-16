import shlex
from dataclasses import dataclass
from typing import Callable

from crawler import crawl_site
from indexer import InvertedIndex, build_index, load_index, save_index
from search import find_pages, format_index_entry, format_search_results

PROMPT = "> "
current_index: InvertedIndex | None = None

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
  global current_index

  verbose = False
  max_pages = None

  if len(args) > 2:
    print("Usage: build [maxPages] [-v]")
    return

  for arg in args:
    if arg == "-v":
      if verbose:
        print("Usage: build [maxPages] [-v]")
        return
      verbose = True
      continue

    if max_pages is not None:
      print("Usage: build [maxPages] [-v]")
      return

    try:
      parsed_max_pages = int(arg)
    except ValueError:
      print("Usage: build [maxPages] [-v]")
      return

    if parsed_max_pages <= 0:
      print("Usage: build [maxPages] [-v]")
      return

    max_pages = parsed_max_pages

  print("Crawling website and extracting page text...")

  pages = crawl_site(verbose=verbose, max_pages=max_pages)
  current_index = build_index(pages)
  save_index(current_index)

  print(f"Crawled {len(pages)} pages and saved index to data/index.json.")


def handle_load(args: list[str]) -> None:
  global current_index

  if args:
    print("Usage: load")
    return

  current_index = load_index()

  if current_index is None:
    print("Could not load index. Run the build command first.")
    return

  page_urls = {
    page_url
    for word_entry in current_index.values()
    for page_url in word_entry
  }

  print("Loaded index from data/index.json.")
  print(f"Indexed words: {len(current_index)}")
  print(f"Indexed pages: {len(page_urls)}")


def handle_print(args: list[str]) -> None:
  if len(args) != 1:
    print("Usage: print <word>")
    return

  if current_index is None:
    print("No index loaded. Run build or load first.")
    return

  word = args[0]
  print(format_index_entry(current_index, word))


def handle_find(args: list[str]) -> None:
  if not args:
    print("Usage: find <string>")
    return

  if current_index is None:
    print("No index loaded. Run build or load first.")
    return

  query = " ".join(args)
  results = find_pages(current_index, query)

  print(format_search_results(results, query))


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