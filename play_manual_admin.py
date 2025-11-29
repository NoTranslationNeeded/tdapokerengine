"""
Master Admin Manual Play Script (God Mode)
Features:
- Configurable N players
- Configurable Blinds & Starting Chips
- Full visibility of all cards
- Manual control for ALL players
"""
import sys
import os
import re

# Add POKERENGINE to path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from poker_engine import PokerGame, Action, ActionType

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_game_state(game: PokerGame):
    print("\n" + "="*100)
    print(f" STREET: {game.street.value.upper()} | POT: {game.get_pot_size():.1f} (Main: {game.pot:.1f})")
    print(f" BOARD:  {', '.join(str(c) for c in game.community_cards) if game.community_cards else 'None'}")
    print("-" * 100)
    print(f"{'ID':<4} {'Role':<8} {'Chips':<10} {'Bet':<10} {'Status':<10} {'Hand':<20}")
    print("-" * 100)
    
    current_actor = game.get_current_player()
    
    for i, p in enumerate(game.players):
        # Determine Role
        role = ""
        if i == game.button_position: role = "BTN"
        
        # Determine SB/BB positions based on player count
        num_players = len(game.players)
        if num_players == 2:
            sb_pos = game.button_position
            bb_pos = (game.button_position + 1) % num_players
        else:
            sb_pos = (game.button_position + 1) % num_players
            bb_pos = (game.button_position + 2) % num_players
            
        if i == sb_pos: role += " SB"
        if i == bb_pos: role += " BB"
        
        # Status
        status = p.state
        if i == current_actor and not game.is_hand_over:
            status = "🔴 ACTING"
        elif p.is_all_in():
            status = "ALL-IN"
        elif p.is_folded():
            status = "FOLDED"
            
        # Hand
        hand_str = f"[{', '.join(str(c) for c in p.hand)}]" if p.hand else "[]"
        if p.is_folded():
            hand_str = "[FOLDED]"
            
        print(f"P{i:<3} {role:<8} {p.chips:<10.1f} {p.bet_this_round:<10.1f} {status:<10} {hand_str:<20}")
        
    print("="*100)

def get_user_action(game: PokerGame, player_id: int) -> Action:
    legal_actions = game.get_legal_actions(player_id)
    legal_str = ", ".join([a.value for a in legal_actions])
    
    current_bet = game.current_bet
    my_bet = game.players[player_id].bet_this_round
    to_call = current_bet - my_bet
    min_raise = game.min_raise
    
    print(f"\n[Player {player_id} Turn]")
    print(f"To Call: {to_call:.1f}")
    if ActionType.RAISE in legal_actions:
        print(f"Min Raise To: {current_bet + min_raise:.1f}")
    
    while True:
        print(f"Legal: [{legal_str}]")
        try:
            raw_input = input(f"Action (P{player_id}) > ").strip().lower()
        except EOFError:
            sys.exit(0)
            
        if not raw_input:
            continue
            
        # Parse input: Handle "r40", "b100", "raise 40"
        cmd = ""
        amount = 0.0
        
        # Check for concatenated format (e.g., r40, b100)
        match = re.match(r"([a-z]+)(\d+(\.\d+)?)", raw_input.split()[0])
        if match:
            cmd = match.group(1)
            amount = float(match.group(2))
        else:
            # Standard space-separated format
            parts = raw_input.split()
            cmd = parts[0]
            amount = float(parts[1]) if len(parts) > 1 else 0.0
        
        try:
            if cmd in ['fold', 'f']:
                return Action.fold()
            elif cmd in ['check', 'ch']:
                return Action.check()
            elif cmd in ['call', 'c']:
                return Action.call(to_call)
            elif cmd in ['bet', 'b']:
                return Action.bet(amount)
            elif cmd in ['raise', 'r']:
                # Input: "raise 300" -> Raise TO 300
                return Action.raise_to(amount)
            elif cmd in ['all', 'allin', 'a']:
                return Action.all_in(game.players[player_id].chips)
            elif cmd in ['quit', 'q', 'exit']:
                sys.exit(0)
            else:
                print("Commands: fold(f), check(ch), call(c), bet(b) <amt>, raise(r) <total_amt>, allin(a)")
        except Exception as e:
            print(f"Error: {e}")

def get_valid_int(prompt: str, min_val: int) -> int:
    while True:
        try:
            val_str = input(f"{prompt}: ").strip()
            if not val_str:
                continue
            val = int(val_str)
            if val < min_val:
                print(f"Value must be at least {min_val}")
                continue
            return val
        except ValueError:
            print("Invalid integer")

def get_valid_float(prompt: str, min_val: float) -> float:
    while True:
        try:
            val_str = input(f"{prompt}: ").strip()
            if not val_str:
                continue
            val = float(val_str)
            if val < min_val:
                print(f"Value must be at least {min_val}")
                continue
            return val
        except ValueError:
            print("Invalid number")

def main():
    print("="*50)
    print(" MASTER ADMIN POKER (GOD MODE)")
    print("="*50)
    
    # Configuration
    num_players = get_valid_int("Number of players (min 2)", 2)
    start_chips = get_valid_float("Starting chips (min 100)", 100.0)
    sb_val = get_valid_float("Small Blind (min 1)", 1.0)
    bb_val = get_valid_float(f"Big Blind (min {sb_val})", sb_val)
    
    game = PokerGame(small_blind=sb_val, big_blind=bb_val)
    
    # Initialize chips for all players
    player_chips = [start_chips] * num_players
    button = 0
    
    while True:
        clear_screen()
        print(f"\n--- NEW HAND --- (Button: P{button})")
        
        # Remove busted players? Or keep them with 0 chips (they won't be dealt in)?
        # Engine expects chip counts for NEW hand.
        # If we pass 0 chips, Player class might handle it or error.
        # Let's filter out busted players or reset them?
        # For Admin Mode, let's keep busted players as 0 and see if engine handles it.
        # Actually, start_hand re-initializes players list.
        # We need to maintain chip counts between hands.
        
        try:
            game.start_hand(player_chips, button)
        except ValueError as e:
            print(f"Error starting hand: {e}")
            break
            
        while not game.is_hand_over:
            print_game_state(game)
            
            current_player = game.get_current_player()
            if current_player == -1:
                # Should not happen in loop unless hand is over
                break
                
            action = get_user_action(game, current_player)
            
            success, error = game.process_action(current_player, action)
            if not success:
                print(f"\n❌ Invalid Action: {error}")
                input("Press Enter to continue...")
            else:
                print(f"\n✅ Action accepted: {action}")
                # input("Press Enter...") 
        
        # Hand over
        print_game_state(game)
        
        if game.winner is not None:
             print(f"\n🏆 Hand Over! Winner: Player {game.winner}")
        else:
             print(f"\n🤝 Hand Over! Split Pot or Showdown")
             
        print("Hand History:")
        for line in game.get_hand_history():
            print(f"  {line}")
            
        # Update chips for next hand
        # game.players has the updated state
        # We need to map back to player_chips list
        # game.players[i] corresponds to player_chips[i] because we initialized in order
        for i, p in enumerate(game.players):
            player_chips[i] = p.chips
            
        # Check for busted players
        active_count = sum(1 for c in player_chips if c > 0)
        if active_count < 2:
            print("\nGame Over! Only one player remaining.")
            break
            
        if input("\nPlay another hand? (y/n) > ").lower() != 'y':
            break
            
        # Move button
        # In N-player, button moves to next active player?
        # Simple logic: Button + 1
        button = (button + 1) % num_players
        # If button player is busted?
        # Advanced logic needed for dead button, but for now simple rotation.

if __name__ == "__main__":
    main()
