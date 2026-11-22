"""CLI: ticket code parsing and menu input handling."""

import pytest

from helpdesk.cli.menu import ConsoleMenu, _read_menu_choice, parse_ticket_code


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("HD-3", 3),
        (" hd-42 ", 42),
        ("HD-0007", 7),
        ("7", None),
        ("HD-", None),
        ("HD-abc", None),
        ("", None),
        (None, None),
    ],
)
def test_parse_ticket_code(raw, expected):
    assert parse_ticket_code(raw) == expected


def test_read_menu_choice_strips_whitespace(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "  2  ")
    assert _read_menu_choice() == "2"


def test_read_menu_choice_exits_cleanly_on_eof(monkeypatch):
    def eof(_):
        raise EOFError

    monkeypatch.setattr("builtins.input", eof)
    with pytest.raises(SystemExit) as caught:
        _read_menu_choice()
    assert caught.value.code == 0


def test_menu_exit_choice_stops_the_loop(monkeypatch, capsys):
    choices = iter(["0"])
    monkeypatch.setattr("builtins.input", lambda _: next(choices))
    ConsoleMenu(service=None, assignment_service=None).run()
    assert "Bye." in capsys.readouterr().out


def test_menu_unknown_choice_is_handled(monkeypatch, capsys):
    choices = iter(["x", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(choices))
    ConsoleMenu(service=None, assignment_service=None).run()
    output = capsys.readouterr().out
    assert "Unknown option." in output


def _ticket_for_assignment(service):
    return service.create_ticket(
        title="Assignment input test",
        description="A ticket used by the CLI assignment input tests.",
        category="TECHNICAL",
        component="email",
    )


def test_assignment_accepts_the_literal_word_auto(monkeypatch, capsys,
                                                  service, assignment, staff_repository):
    staff_repository.add("Maya Chen")
    ticket = _ticket_for_assignment(service)
    choices = iter(["5", f"HD-{ticket.id:04d}", "AUTO", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(choices))

    ConsoleMenu(service, assignment).run()

    output = capsys.readouterr().out
    assert f"Assigned HD-{ticket.id:04d} -> staff #1." in output


def test_assignment_rejects_non_numeric_input_without_crashing(monkeypatch, capsys,
                                                               service, assignment,
                                                               staff_repository):
    staff_repository.add("Maya Chen")
    ticket = _ticket_for_assignment(service)
    choices = iter(["5", f"HD-{ticket.id:04d}", "abc", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(choices))

    ConsoleMenu(service, assignment).run()

    output = capsys.readouterr().out
    assert "Not a staff id: 'abc'" in output
    assert "Bye." in output
