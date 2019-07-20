from random import *
from os import system, name

values = ["Ace", 2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King"]
suits = ["Hearts", "Diamonds", "Spades", "Clubs"]

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.next_card = None
        self.is_face_down = False

    def __str__(self):
        return str(self.value) + " of " + self.suit

class Deck:
    def __init__(self, limit=52):
        self.size = 0
        self.limit = limit
        self.top_card = None

    def __str__(self):
        return_string = ""
        card_for_printing = self.top_card
        while card_for_printing:
            return_string += str(card_for_printing) + "\n"
            card_for_printing = card_for_printing.next_card
        return return_string
    
    def prepare_deck(self):
        self.fill_deck()
        self.shuffle()

    def fill_deck(self):
        for value in values:
            for suit in suits:
                new_card = Card(value, suit)
                self.push_card(new_card)

    def empty_deck(self):
        self.top_card = None
        self.size = 0

    def push_card(self, card):
        if self.size < self.limit:
            card.next_card = self.top_card
            self.top_card = card
            self.size += 1
        else:
            print("Already " + self.limit + " cards in deck!")

    def pop_card(self):
        return_card = self.top_card
        self.top_card = return_card.next_card
        self.size -= 1
        return return_card

    def pluck_card(self):
        index = randint(0, self.size-1)
        if index == 0:
            return self.pop_card()
        current_card = self.top_card
        for i in range(index):
            previous_card = current_card
            current_card = previous_card.next_card
        previous_card.next_card = current_card.next_card
        self.size -= 1
        return current_card

    def shuffle(self):
        new_deck = Deck()
        new_deck.size, new_deck.limit, new_deck.top_card = self.size, self.limit, self.top_card
        self.empty_deck()
        while new_deck.size > 0:
            self.push_card(new_deck.pluck_card())

class Dealer:
    def __init__(self):
        self.hand = None
        self.deck = Deck()
        self.prepare_deck()

    def __str__(self):
        return str(self.hand)

class Player:
    def __init__(self, dealer):
        self.hands = []
        self.dealer = None
        self.chips = 0
        self.bet = bet
        self.double_down = False
        self.insurance = False

    def __str__(self):
        string = "Funds: " + str(self.chips) + "\n"
        for hand in hands:
            string += str(hand) + "\n"
        return string

    def play_hand(self):
        bet = enter_positive_integer("How many chips would you like to bet? Enter whole number: ")
        new_hand = PlayerHand(self, bet)
        self.hands.append(new_hand)
        self.dealer.hand = DealerHand(self.dealer)
        for i in range(2):
            self.dealer.hand.get_card()
            self.hands[0].get_card()
        self.dealer.hand.face_down_head_card()
        self.print_table()
        if self.dealer.hand.has_soft_ace():
            if enter_YorN("Would you like to take insurance? Y or N"):
                self.insurance = True
                self.print_table()
        if enter_YorN("Would you like to double down? Y or N"):
            self.double_down = True
            self.bet = self.bet*2
            self.hands[0].get_card()
            self.print_table()
        else:

    def print_table(self):
        def find_largest_hand_size():
            largest_hand_size = self.dealer.hand.size
            for hand in self.hands:
                if hand.size > largest_hand_size:
                    largest_hand_size = hand.size
            return largest_hand_size

        clear()
        string = "Current Bet: {}\n".format(self.bet)
        if self.insurance:
            string += "Insured\n\n"
        else:
            string += "\n\n"
        string += "Dealer:"
        for hand in self.hands:
            string += "\t\t\tPlayer:"
        string += "\n"
        all_hands = [self.dealer.hand] + self.hands
        largest_hand_size = find_largest_hand_size()
        for i in range(largest_hand_size):
            for hand in all_hands:
                card = hand.head_card
                counter = 0
                while i > counter:
                    card = card.next_card
                temp_string = str(card)
                spaces = 24 - len(temp_string)
                spaces_string = ""
                counter = 0
                while spaces > counter:
                    spaces_string += " "
                string += temp_string + spaces_string
        for hand in all_hands:
            total, soft_ace = hand.calculate_hand()
            temp_string = "Total: {}".format(total)
            if soft_ace:
                temp_string += "Soft Ace"
            spaces = 24 - len(temp_string)
            spaces_string = ""
            counter = 0
            while spaces > counter:
                spaces_string += " "
            string += temp_string + spaces_string
        print(string)

    def add_chips(self):
        print("You have {} chips.".format(self.chips))
        self.chips += enter_positive_integer("How many more chips would you like? Enter whole number: ")
        clear()
        print("Now you have {} chips.".format(self.chips))
        isenough = enter_YorN("Is that enough? Y or N: ")
        if not isenough:
            clear()
            self.add_chips()
        clear()

    def withdraw_chips(self, chips_to_withdraw):
        self.chips -= chips_to_withdraw

class Hand:
    def __init__(self, owner):
        self.head_card = None
        self.size = 0
        self.owner = owner

    def __str__(self):
        string = ""
        card = self.head_card
        while card:
            string += str(card) + "\n"
            card = card.next_card
        return string

    def calculate_hand(self):
        total = 0
        soft_ace = False
        card = self.head_card
        while card:
            if card.is_face_down:
                continue
            if isinstance(card.value, int):
                total += card.value
            elif card.value == "Jack" or card.value == "Queen" or card.value == "King":
                total += 10
            else:
                if soft_ace:
                    total += 1
                else:
                    total += 11
                    soft_ace = True
            while total > 21:
                if soft_ace:
                    total -= 10
                    soft_ace = False
                else:
                    return -1
            card = card.next_card
        return total, soft_ace

    def calculate_total(self):
        total, soft_ace = self.calculate_hand()
        return total

    def has_soft_ace(self):
        total, soft_ace = self.calculate_hand()
        return soft_ace

class PlayerHand(Hand):
    def __init__(self, owner, bet):
        self.head_card = None
        self.owner = owner

    def outcome(self, outcome):

    def get_card(self):
        card = self.owner.dealer.deck.pop_card()
        card.next_card = self.head_card
        self.head_card = card
        self.size += 1

class DealerHand(Hand):
    def __str__(self):
        string = ""
        card = self.head_card
        while card:
            if card.is_face_down:
                string += "*Card Face Down*" + "\n"
            else:
                string += str(card) + "\n"
            card = card.next_card
        return string

    def get_card(self):
        card = self.owner.deck.pop_card()
        card.next_card = self.head_card
        self.head_card = card
        self.size += 1

    def face_down_head_card(self):
        self.head_card.is_face_down = True

def clear():
    os.system('cls')

def enter_casino():
    clear()
    print("Welcome to the casino!")
    print("You need chips to play Blackjack. Press enter to continue: ")
    input("")
    clear()

def enter_positive_integer(string):
    result = input(string)
    while (not isinstance(result, int)) or result < 0:
        clear()
        if not isinstance(result, int):
            print("Invalid input. Must be whole number.")
        elif result < 0:
            print("Invalid input. Must be positive number.")
        result = input(string)
    return result

def enter_YorN(string):
    result = input(string)
    while result != "Y" or result != "N" or result != "y" or result != "n":
        clear()
        print("Invalid input.")
        result = input(string)
    if result == "Y" or result == "y":
        result = True
    else:
        result = False
    return result

dealer = Dealer()
player = Player(dealer)
enter_casino()
player.add_chips()
print("Here is your table, have fun! Press enter to continue: ")
input("")
clear()
while exit:
    player.play_hand()
