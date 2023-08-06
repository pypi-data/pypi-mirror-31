import pytest

from pyschieber.rules.stich_rules import stich_rules, card_allowed, allowed_cards, is_trumpf_under, does_under_trumpf, \
    is_chosen_card_best_trumpf
from pyschieber.trumpf import Trumpf
from pyschieber.card import Card
from pyschieber.player.random_player import RandomPlayer
from pyschieber.stich import PlayedCard
from pyschieber.suit import Suit


@pytest.fixture(scope="module", autouse=True)
def players():
    return [RandomPlayer(), RandomPlayer(), RandomPlayer(), RandomPlayer()]


@pytest.fixture(scope="module", autouse=True)
def played_cards(players):
    return [PlayedCard(player=players[0], card=Card(Suit.BELL, 10)),
            PlayedCard(player=players[1], card=Card(Suit.ACORN, 6)),
            PlayedCard(player=players[2], card=Card(Suit.BELL, 13)),
            PlayedCard(player=players[3], card=Card(Suit.BELL, 9))]


@pytest.mark.parametrize("trumpf, index,", [
    (Trumpf.OBE_ABE, 2),
    (Trumpf.UNDE_UFE, 3),
    (Trumpf.BELL, 3),
    (Trumpf.ACORN, 1),
])
def test_stich(trumpf, index, players, played_cards):
    stich = stich_rules[trumpf](played_cards=played_cards)
    assert stich.player is players[index]


@pytest.mark.parametrize("table_cards, chosen_card, hand_cards, trumpf, result", [
    ([Card(Suit.ACORN, 12)], Card(Suit.BELL, 12), [Card(Suit.ACORN, 11), Card(Suit.BELL, 12), Card(Suit.BELL, 11)],
     Trumpf.OBE_ABE, False),
    ([Card(Suit.BELL, 12)], Card(Suit.BELL, 12), [Card(Suit.BELL, 12), Card(Suit.BELL, 11)], Trumpf.BELL, True),
    (None, Card(Suit.BELL, 12), [Card(Suit.BELL, 12), Card(Suit.BELL, 11)], Trumpf.BELL, True),
    ([Card(Suit.BELL, 12)], Card(Suit.BELL, 12), [Card(Suit.BELL, 12), Card(Suit.BELL, 11)], Trumpf.OBE_ABE, True),
    ([Card(Suit.ACORN, 12)], Card(Suit.BELL, 12), [Card(Suit.BELL, 12), Card(Suit.BELL, 11)], Trumpf.OBE_ABE, True),
    ([Card(Suit.ACORN, 11)], Card(Suit.BELL, 12), [Card(Suit.ACORN, 12), Card(Suit.BELL, 11), Card(Suit.BELL, 12)],
     Trumpf.ACORN, False),
    ([Card(Suit.ACORN, 11)], Card(Suit.ACORN, 11), [Card(Suit.BELL, 12), Card(Suit.ACORN, 11), Card(Suit.ACORN, 12)],
     Trumpf.UNDE_UFE, True),
    ([Card(Suit.ACORN, 11)], Card(Suit.ACORN, 11), [Card(Suit.BELL, 12), Card(Suit.ACORN, 12)],
     Trumpf.UNDE_UFE, False),
    ([Card(Suit.ROSE, 6)], Card(Suit.ACORN, 11), [Card(Suit.ROSE, 10), Card(Suit.ACORN, 11)],
     Trumpf.ROSE, False),
    ([Card(Suit.ROSE, 6)], Card(Suit.ACORN, 11), [Card(Suit.ROSE, 11), Card(Suit.ACORN, 11)],
     Trumpf.ROSE, True),
])
def test_card_allowed(table_cards, chosen_card, hand_cards, trumpf, result):
    assert card_allowed(table_cards, chosen_card, hand_cards, trumpf) == result


@pytest.mark.parametrize("hand_cards, table_cards, trumpf, result", [
    ([Card(Suit.BELL, 12)], [Card(Suit.BELL, 11)], Trumpf.BELL, [Card(Suit.BELL, 12)]),
    ([Card(Suit.BELL, 12), Card(Suit.ROSE, 12)], [Card(Suit.BELL, 11)], Trumpf.ACORN, [Card(Suit.BELL, 12)]),
    ([Card(Suit.BELL, 12)], [Card(Suit.ROSE, 11)], Trumpf.ACORN, [Card(Suit.BELL, 12)]),
])
def test_allowed_cards(hand_cards, table_cards, trumpf, result):
    assert allowed_cards(hand_cards=hand_cards, table_cards=table_cards, trumpf=trumpf) == result


@pytest.mark.parametrize("trumpf, card, result", [
    (Trumpf.BELL, Card(Suit.BELL, 12), False),
    (Trumpf.BELL, Card(Suit.BELL, 11), True),
    (Trumpf.ROSE, Card(Suit.BELL, 11), False),
    (Trumpf.OBE_ABE, Card(Suit.BELL, 11), False),
    (Trumpf.ROSE, Card(Suit.ROSE, 11), True),
])
def test_is_trumpf_under(trumpf, card, result):
    assert is_trumpf_under(trumpf=trumpf, card=card) == result


@pytest.mark.parametrize("table_cards, chosen_card, hand_cards, trumpf, result", [
    ([Card(Suit.ACORN, 12)], Card(Suit.BELL, 12), [Card(Suit.BELL, 12)], Trumpf.OBE_ABE, False),
    ([Card(Suit.ACORN, 12)], Card(Suit.ACORN, 6), [Card(Suit.ACORN, 6), Card(Suit.BELL, 6)], Trumpf.ACORN, True),
    ([Card(Suit.ACORN, 12)], Card(Suit.ACORN, 13), [Card(Suit.ACORN, 13)], Trumpf.ACORN, False),
    ([Card(Suit.BELL, 12)], Card(Suit.BELL, 13), [Card(Suit.BELL, 13)], Trumpf.BELL, False),
    ([Card(Suit.BELL, 12)], Card(Suit.BELL, 6), [Card(Suit.BELL, 6), Card(Suit.ROSE, 6)], Trumpf.BELL, True),
    ([Card(Suit.BELL, 12)], Card(Suit.BELL, 6), [Card(Suit.BELL, 6), Card(Suit.BELL, 7)], Trumpf.BELL, False),
])
def test_does_under_trumpf(table_cards, chosen_card, hand_cards, trumpf, result):
    assert does_under_trumpf(table_cards, chosen_card, hand_cards, trumpf) == result


@pytest.mark.parametrize("table_cards, chosen_card, trumpf, result", [
    ([Card(Suit.ACORN, 12)], Card(Suit.ACORN, 11), Trumpf.ACORN, True),
    ([Card(Suit.ACORN, 11)], Card(Suit.ACORN, 12), Trumpf.ACORN, False),
    ([Card(Suit.ACORN, 13), Card(Suit.ACORN, 14)], Card(Suit.ACORN, 6), Trumpf.ACORN, False),
    ([Card(Suit.ACORN, 13), Card(Suit.ACORN, 14)], Card(Suit.ACORN, 11), Trumpf.ACORN, True),
])
def test_is_chosen_card_best_trumpf(table_cards, chosen_card, trumpf, result):
    assert is_chosen_card_best_trumpf(table_cards, chosen_card, trumpf) == result
