#!/usr/bin/env python3
"""Interactive tester for the Activepieces pieces database helper."""

from __future__ import annotations

import sys
from typing import Callable, Dict

from activepieces_db import ActivepiecesDB


def _prompt(message: str) -> str:
    try:
        return input(message).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting…")
        sys.exit(0)


def _prompt_positive_int(message: str, default: int) -> int:
    raw = _prompt(message)
    if not raw:
        return default
    try:
        value = int(raw)
        if value <= 0:
            raise ValueError
    except ValueError:
        print(f"Invalid number '{raw}'. Using default {default}.")
        return default
    return value


def run_search_pieces(db: ActivepiecesDB) -> None:
    query = _prompt("Enter search terms for pieces: ")
    if not query:
        print("No query provided. Returning to menu.\n")
        return
    limit = _prompt_positive_int("How many results? [default 10]: ", 10)
    print()
    results = db.search_pieces(query, limit=limit)
    if not results:
        print("No pieces found.\n")
        return
    print(f"Found {len(results)} piece(s):")
    for idx, piece in enumerate(results, 1):
        print(
            f"  {idx}. {piece['display_name']} ({piece['name']}) — "
            f"{piece['action_count']} actions, {piece['trigger_count']} triggers"
        )
    print()


def run_search_actions(db: ActivepiecesDB) -> None:
    query = _prompt("Enter search terms for actions: ")
    if not query:
        print("No query provided. Returning to menu.\n")
        return
    limit = _prompt_positive_int("How many results? [default 10]: ", 10)
    print()
    results = db.search_actions(query, limit=limit)
    if not results:
        print("No actions found.\n")
        return
    print(f"Found {len(results)} action(s):")
    for idx, action in enumerate(results, 1):
        print(
            f"  {idx}. {action['piece_display_name']} • {action['action_display_name']}"
        )
        if action.get("description"):
            print(f"     {action['description']}")
        print(f"     Requires auth: {action['requires_auth']}")
    print()


def run_piece_details(db: ActivepiecesDB) -> None:
    piece_name = _prompt("Enter the piece name (e.g. gmail): ")
    if not piece_name:
        print("No piece name provided. Returning to menu.\n")
        return
    print()
    piece = db.get_piece_details(piece_name)
    if not piece:
        print(f"Piece '{piece_name}' not found.\n")
        return
    print(f"Details for {piece['display_name']} ({piece['name']}):")
    print(f"  Auth type: {piece.get('auth_type', 'unknown')}")
    categories = piece.get('categories') or []
    if categories:
        print(f"  Categories: {', '.join(categories)}")
    print(f"  Actions: {len(piece['actions'])}")
    for action in piece['actions'][:10]:
        print(f"    • {action['display_name']} ({action['name']})")
    if len(piece['actions']) > 10:
        print("    …")
    print(f"  Triggers: {len(piece['triggers'])}")
    for trigger in piece['triggers'][:10]:
        print(f"    • {trigger['display_name']} ({trigger['name']})")
    if len(piece['triggers']) > 10:
        print("    …")
    print()


def run_action_inputs(db: ActivepiecesDB) -> None:
    piece_name = _prompt("Enter the piece name (e.g. gmail): ")
    if not piece_name:
        print("No piece name provided. Returning to menu.\n")
        return
    action_name = _prompt("Enter the action name (e.g. send_email): ")
    if not action_name:
        print("No action name provided. Returning to menu.\n")
        return
    print()
    inputs = db.get_action_inputs(piece_name, action_name)
    if not inputs:
        print("No input properties found. Check the piece and action names.\n")
        return
    print(
        f"Input properties for {piece_name}.{action_name} (total {len(inputs)}):"
    )
    for prop in inputs:
        required = "required" if prop['required'] else "optional"
        default = prop.get('default_value')
        default_str = f" (default: {default})" if default not in (None, "") else ""
        print(
            f"  • {prop['display_name']} ({prop['name']}) — "
            f"{prop['type']} {required}{default_str}"
        )
        if prop.get("description"):
            print(f"    {prop['description']}")
    print()


def run_top_pieces(db: ActivepiecesDB) -> None:
    limit = _prompt_positive_int("How many top pieces? [default 10]: ", 10)
    print()
    results = db.get_top_pieces(limit=limit)
    if not results:
        print("No pieces returned.\n")
        return
    print("Top pieces by total capabilities:")
    for idx, piece in enumerate(results, 1):
        total = piece['action_count'] + piece['trigger_count']
        print(
            f"  {idx}. {piece['display_name']} — "
            f"{piece['action_count']} actions / {piece['trigger_count']} triggers"
        )
        print(f"     Total capabilities: {total}")
    print()


def run_pieces_by_auth(db: ActivepiecesDB) -> None:
    auth_type = _prompt("Enter auth type (e.g. OAuth2, ApiKey, SecretText): ")
    if not auth_type:
        print("No auth type provided. Returning to menu.\n")
        return
    limit = _prompt_positive_int(
        "How many results? [default 20]: ",
        20,
    )
    print()
    results = db.get_pieces_by_auth_type(auth_type)
    if not results:
        print(f"No pieces found for auth type '{auth_type}'.\n")
        return
    print(f"Pieces with auth type '{auth_type}':")
    for idx, piece in enumerate(results[:limit], 1):
        total = piece['action_count'] + piece['trigger_count']
        print(
            f"  {idx}. {piece['display_name']} — {piece['action_count']} actions, "
            f"{piece['trigger_count']} triggers (total {total})"
        )
    if len(results) > limit:
        print(f"  … {len(results) - limit} more not shown")
    print()


def main() -> None:
    actions: Dict[str, Callable[[ActivepiecesDB], None]] = {
        "1": run_search_pieces,
        "2": run_search_actions,
        "3": run_piece_details,
        "4": run_action_inputs,
        "5": run_top_pieces,
        "6": run_pieces_by_auth,
    }

    print("=== Activepieces Tools Tester ===")
    print("Connects to activepieces-pieces.db and runs helper methods.\n")

    with ActivepiecesDB() as db:
        while True:
            print("Choose a tool: ")
            print("  1) Search pieces")
            print("  2) Search actions")
            print("  3) Piece details")
            print("  4) Action inputs")
            print("  5) Top pieces")
            print("  6) Pieces by auth type")
            print("  0) Exit")

            choice = _prompt("Select option [0-6]: ")
            print()

            if choice == "0":
                print("Goodbye!")
                return

            handler = actions.get(choice)
            if handler is None:
                print("Invalid option. Please choose again.\n")
                continue

            handler(db)


if __name__ == "__main__":
    main()


