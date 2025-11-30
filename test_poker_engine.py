"""
Unit tests for TDA Poker Engine
Tests all core functionality with current API
"""
import sys
sys.path.insert(0, '.')

from poker_engine import Card, Deck, Player, Action, ActionType, PokerGame
from poker_engine.evaluator import HandEvaluator


def test_card_and_deck():
    """Test card and deck basic functionality"""
    print("Testing Card and Deck...")
    
    # Test card creation
    card = Card('S', 'A')
    assert str(card) == 'SA'
    assert card.pretty_str() == '♠A'
    
    # Test deck
    deck = Deck()
    assert len(deck) == 52
    
    # Test dealing
    hand = deck.deal(2)
    assert len(hand) == 2
    assert len(deck) == 50
    
    print("✓ Card and Deck tests passed")


def test_player():
    """Test player functionality"""
    print("\nTesting Player...")
    
    player = Player(0, 1000)
    assert player.chips == 1000
    assert player.is_active()
    assert player.last_action is None
    
    # Test betting
    player.place_bet(100)
    assert player.chips == 900
    assert player.bet_this_round == 100
    
    # Test fold
    player.fold()
    assert player.is_folded()
    assert not player.can_bet()
    
    print("✓ Player tests passed")


def test_hand_evaluator():
    """Test hand evaluation and best 5 cards"""
    print("\nTesting HandEvaluator...")
    
    # Test Royal Flush
    hand = [Card('S', 'A'), Card('S', 'K')]
    board = [Card('S', 'Q'), Card('S', 'J'), Card('S', 'T'), Card('H', '2'), Card('D', '3')]
    
    value = HandEvaluator.evaluate(hand, board)
    name = HandEvaluator.get_hand_name(hand, board)
    best_five = HandEvaluator.get_best_five(hand, board)
    
    assert name == "Straight Flush"
    assert len(best_five) == 5
    
    # Test High Card
    hand2 = [Card('S', 'A'), Card('H', '2')]
    board2 = [Card('D', '5'), Card('C', '7'), Card('S', '9'), Card('H', 'J'), Card('D', 'K')]
    
    value2 = HandEvaluator.evaluate(hand2, board2)
    name2 = HandEvaluator.get_hand_name(hand2, board2)
    
    assert name2 == "High Card"
    assert value > value2  # Royal flush should beat high card
    
    print("✓ HandEvaluator tests passed")


def test_basic_game():
    """Test basic poker game with new API"""
    print("\nTesting Basic PokerGame...")
    
    game = PokerGame(small_blind=50, big_blind=100)
    
    # New API: pass list of chips
    game.start_hand(players_info=[1000, 1000], button=0)
    
    # Check initial state
    assert game.street.value == 'preflop'
    assert len(game.players) == 2
    assert len(game.players[0].hand) == 2
    assert len(game.players[1].hand) == 2
    
    # Check blinds posted (Button = P0 = SB, P1 = BB)
    assert game.players[0].bet_this_round == 50
    assert game.players[1].bet_this_round == 100
    assert game.players[0].last_action == "Post SB"
    assert game.players[1].last_action == "Post BB"
    
    # P0 (SB) calls
    success, error = game.process_action(0, Action.call(50))
    assert success, f"Call should succeed: {error}"
    assert game.players[0].last_action == "Call 50"
    
    # BB checks (check last_action before street advances)
    success, error = game.process_action(1, Action.check())
    assert success, f"Check should succeed: {error}"
    # Note: last_action is reset when advancing to new street
    
    # Should advance to flop
    assert game.street.value == 'flop'
    assert len(game.community_cards) == 3
    
    # Check that last_action was reset for new street
    assert game.players[0].last_action is None
    assert game.players[1].last_action is None
    
    print("✓ Basic PokerGame tests passed")


def test_multiplayer():
    """Test multi-player game (3+ players)"""
    print("\nTesting Multi-player Game...")
    
    game = PokerGame(small_blind=10, big_blind=20)
    
    # 4 players with IDs
    game.start_hand(players_info=[(0, 1000), (1, 1000), (2, 1000), (3, 1000)], button=0)
    
    assert len(game.players) == 4
    assert game.players[1].last_action == "Post SB"
    assert game.players[2].last_action == "Post BB"
    
    print("✓ Multi-player tests passed")


def test_raise_tracking():
    """Test last_action for raises"""
    print("\nTesting Raise Action Tracking...")
    
    game = PokerGame(small_blind=10, big_blind=20)
    game.start_hand([1000, 1000], button=0)
    
    # SB raises
    game.process_action(0, Action.raise_to(60))
    assert game.players[0].last_action == "Raise To 60"
    
    # BB folds
    game.process_action(1, Action.fold())
    assert game.players[1].last_action == "FOLDED"
    
    print("✓ Raise tracking tests passed")


def test_unicode_display():
    """Test Unicode suit display"""
    print("\nTesting Unicode Suit Display...")
    
    card = Card('H', 'A')
    assert card.pretty_str() == '♥A'
    
    card2 = Card('S', 'K')
    assert card2.pretty_str() == '♠K'
    
    card3 = Card('D', 'Q')
    assert card3.pretty_str() == '♦Q'
    
    card4 = Card('C', 'J')
    assert card4.pretty_str() == '♣J'
    
    print("✓ Unicode display tests passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running TDA Poker Engine Tests")
    print("=" * 60)
    
    try:
        test_card_and_deck()
        test_player()
        test_hand_evaluator()
        test_basic_game()
        test_multiplayer()
        test_raise_tracking()
        test_unicode_display()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED (7/7)")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
