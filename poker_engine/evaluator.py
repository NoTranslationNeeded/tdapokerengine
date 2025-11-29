"""
Hand Evaluator (Pure Python Implementation)
Replaces eval7 dependency with a standalone evaluator.
"""
from typing import List
from .cards import Card
from collections import Counter

class HandEvaluator:
    """
    Evaluates poker hands using pure Python logic.
    Returns an integer score (higher is better).
    """
    
    # Rank values for evaluation
    RANK_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    
    # Hand categories (higher is better)
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9
    
    @staticmethod
    def evaluate(hole_cards: List[Card], community_cards: List[Card]) -> int:
        """
        Evaluate hand strength.
        Returns an integer representing the hand strength.
        Format: (Category << 20) | (Tiebreakers...)
        """
        all_cards = hole_cards + community_cards
        if not all_cards:
            return 0
            
        # Convert to easier format for processing
        # (rank_value, suit_char)
        processed_cards = []
        for card in all_cards:
            processed_cards.append((HandEvaluator.RANK_VALUES[card.rank], card.suit))
            
        # Get best 5-card hand score
        return HandEvaluator._get_score(processed_cards)

    @staticmethod
    def get_hand_name(hole_cards: List[Card], community_cards: List[Card]) -> str:
        """Get string representation of the best hand rank"""
        score = HandEvaluator.evaluate(hole_cards, community_cards)
        category = score >> 20
        
        names = {
            0: "High Card",
            1: "Pair",
            2: "Two Pair",
            3: "Three of a Kind",
            4: "Straight",
            5: "Flush",
            6: "Full House",
            7: "Four of a Kind",
            8: "Straight Flush",
            9: "Royal Flush"
        }
        return names.get(category, "Unknown")

    @staticmethod
    def _get_score(cards):
        """
        Calculate score for 5 best cards out of 7 (or fewer).
        Returns integer score.
        """
        # Sort by rank descending
        cards.sort(key=lambda x: x[0], reverse=True)
        
        # Check Flush
        suits = [c[1] for c in cards]
        suit_counts = Counter(suits)
        flush_suit = None
        for suit, count in suit_counts.items():
            if count >= 5:
                flush_suit = suit
                break
        
        if flush_suit:
            flush_cards = [c for c in cards if c[1] == flush_suit]
            # Check Straight Flush
            sf_score = HandEvaluator._check_straight([c[0] for c in flush_cards])
            if sf_score:
                return (HandEvaluator.STRAIGHT_FLUSH << 20) | sf_score
            
            # Regular Flush
            # Take top 5 cards
            score = HandEvaluator.FLUSH << 20
            for i in range(5):
                score |= (flush_cards[i][0] << (16 - i*4))
            return score
            
        # Check Straight
        ranks = [c[0] for c in cards]
        straight_score = HandEvaluator._check_straight(ranks)
        if straight_score:
            return (HandEvaluator.STRAIGHT << 20) | straight_score
            
        # Check Pairs/Trips/Quads
        rank_counts = Counter(ranks)
        sorted_counts = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
        
        # Four of a Kind
        if sorted_counts[0][1] == 4:
            # 4 of a kind + 1 kicker
            score = (HandEvaluator.FOUR_OF_A_KIND << 20)
            score |= (sorted_counts[0][0] << 16)
            # Find kicker
            kicker = 0
            for r, c in sorted_counts[1:]:
                kicker = r
                break
            score |= (kicker << 12)
            return score
            
        # Full House
        if sorted_counts[0][1] == 3 and len(sorted_counts) > 1 and sorted_counts[1][1] >= 2:
            score = (HandEvaluator.FULL_HOUSE << 20)
            score |= (sorted_counts[0][0] << 16) # Trips part
            score |= (sorted_counts[1][0] << 12) # Pair part
            return score
            
        # Three of a Kind
        if sorted_counts[0][1] == 3:
            score = (HandEvaluator.THREE_OF_A_KIND << 20)
            score |= (sorted_counts[0][0] << 16)
            # Kickers
            kickers = []
            for r, c in sorted_counts[1:]:
                kickers.append(r)
            for i in range(min(2, len(kickers))):
                score |= (kickers[i] << (12 - i*4))
            return score
            
        # Two Pair
        if sorted_counts[0][1] == 2 and len(sorted_counts) > 1 and sorted_counts[1][1] == 2:
            score = (HandEvaluator.TWO_PAIR << 20)
            score |= (sorted_counts[0][0] << 16)
            score |= (sorted_counts[1][0] << 12)
            # Kicker
            kicker = 0
            for r, c in sorted_counts[2:]:
                kicker = r
                break
            score |= (kicker << 8)
            return score
            
        # Pair
        if sorted_counts[0][1] == 2:
            score = (HandEvaluator.PAIR << 20)
            score |= (sorted_counts[0][0] << 16)
            # Kickers
            kickers = []
            for r, c in sorted_counts[1:]:
                kickers.append(r)
            for i in range(min(3, len(kickers))):
                score |= (kickers[i] << (12 - i*4))
            return score
            
        # High Card
        score = (HandEvaluator.HIGH_CARD << 20)
        for i in range(min(5, len(ranks))):
            score |= (ranks[i] << (16 - i*4))
        return score

    @staticmethod
    def _check_straight(ranks: List[int]) -> int:
        """
        Check for straight in list of ranks (descending).
        Returns score (highest rank) or 0.
        """
        unique_ranks = sorted(list(set(ranks)), reverse=True)
        
        # Check normal straights
        for i in range(len(unique_ranks) - 4):
            if unique_ranks[i] - unique_ranks[i+4] == 4:
                return unique_ranks[i]
                
        # Check Wheel (A-5-4-3-2)
        # A is 14. If we have 14, 5, 4, 3, 2
        if 14 in unique_ranks and 5 in unique_ranks and 4 in unique_ranks and 3 in unique_ranks and 2 in unique_ranks:
            return 5 # 5-high straight
            
        return 0
