from random import *
import os
#from os import system, name

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
        self.deck.prepare_deck()

    def __str__(self):
        return str(self.hand)

class Player:
    def __init__(self, dealer):
        self.hands = []
        self.dealer = dealer
        self.chips = 0
        self.bet = 0
        self.double_down = False
        self.insurance = False

    def __str__(self):
        string = "Funds: " + str(self.chips) + "\n"
        for hand in hands:
            string += str(hand) + "\n"
        return string

    def prepare_for_next_hand(self):
        self.hands = []
        self.double_down = False
        self.insurance = False
        self.dealer.hand = None
        self.dealer.deck = Deck()
        self.dealer.deck.prepare_deck()
        if self.chips <= 0:
            print("You're out of chips! Let's add more. Press enter to continue:")
            clear()
            self.add_chips()

    def play_hand(self):
        while True:
            print("You have {} chips.".format(self.chips))
            self.bet = enter_positive_integer("How many chips would you like to bet? Enter whole number: ")
            if self.bet <= self.chips:
                break
            input("Invalid bet. You cannot bet more than you have chips. Press enter to try again:")
            clear()
        new_hand = PlayerHand(self)
        self.hands.append(new_hand)
        self.dealer.hand = DealerHand(self.dealer)
        for i in range(2):
            self.dealer.hand.get_card()
            self.hands[0].get_card()
        self.dealer.hand.face_down_head_card()
        self.print_table()
        if self.dealer.hand.has_soft_ace():
            if 3*self.bet//2 > self.chips:
                input("You cannot take insurance because you don't have enough chips. Press enter to continue:")
            elif enter_YorN("Would you like to take insurance? Y or N: "):
                self.insurance = True
                self.print_table()
        if 9 <= self.hands[0].calculate_total() and self.hands[0].calculate_total() <= 11:
            if self.bet*2 > self.chips:
                input("You cannot double down because you don't have enough chips. Press enter to continue:")
                self.print_table()
            elif enter_YorN("Would you like to double down? Y or N: "):
                self.double_down = True
                self.bet = self.bet*2
                self.hands[0].get_card()
                self.print_table()
        if not self.double_down:
            try:
                index = 0
                while True:
                    hand = self.hands[index]
                    if not hand.head_card.next_card:
                        hand.get_card()
                    if hand.head_card.value == hand.head_card.next_card.value:
                        if enter_YorN("Doubles! Would you like to split? Y or N: "):
                            new_hand = PlayerHand(self)
                            self.hands.append(new_hand)
                            self.hands[-1].head_card = hand.head_card.next_card
                            self.hands[-1].size = 1
                            hand.head_card.next_card = None
                            hand.size = 1
                    if hand.head_card.next_card == None:
                        hand.get_card()
                    self.print_table()
                    while hand.calculate_total() != "BUST":
                        if enter_YorN("Hit? Y or N: "):
                            hand.get_card()
                            self.print_table()
                        else:
                            self.print_table()
                            break
                    index += 1
            except IndexError:
                pass
        input("Now the Dealer will play. Press enter to reveal the Dealer's face down card:")
        self.dealer.hand.face_up_head_card()
        self.print_table()
        if self.insurance:
            if self.dealer.hand.calculate_total() == 21:
                input("Insurance Succeeded! {} added to chips. Press enter to continue.".format(self.bet))
                self.chips += self.bet
            else:
                input("Insurance Failed! {} taken from chips. Press enter to continue.".format(self.bet//2))
                self.chips -= self.bet//2
            self.insurance = False
            self.print_table()
        while self.dealer.hand.calculate_total() != "BUST" and self.dealer.hand.calculate_total() < 17:
            input("Dealer must hit. Press enter to continue.")
            self.dealer.hand.get_card()
            self.print_table()
        dealer_result = self.dealer.hand.calculate_total()
        if dealer_result == "BUST":
            input("Dealer has busted! Press enter to continue.")
        else:
            input("Dealer has stood at {}. Press enter to continue.".format(dealer_result))
        self.print_table()
        for hand in self.hands:
            if hand.calculate_total() == "BUST":
                input("Player busted on this hand. Player loses {} chips. Press enter to continue.".format(self.bet))
                self.chips -= self.bet
                self.print_table()
            elif hand.size == 2 and hand.calculate_total() == 21:
                input("Player got blackjack! Player wins {} chips. Press enter to continue.".format(int(1.5*self.bet)))
                self.chips += int(1.5*self.bet)
                self.print_table()
            elif dealer_result == "BUST":
                input("Dealer busted and you didn't! You win {} chips. Press enter to continue.".format(self.bet))
                self.chips += self.bet
                self.print_table()
            elif hand.calculate_total() > dealer_result:
                input("Player won! Player wins {} chips. Press enter to continue.".format(self.bet))
                self.chips += self.bet
                self.print_table()
            elif hand.calculate_total() == dealer_result:
                input("Player tied. Player gains nor loses chips. Press enter to continue.")
                self.print_table()
            else:
                input("Player lost. Player loses {} chips. Press enter to continue.".format(self.bet))
                self.chips -= self.bet
                self.print_table()
        clear()

    def print_table(self):
        def find_largest_hand_size():
            largest_hand_size = self.dealer.hand.size
            for hand in self.hands:
                if hand.size > largest_hand_size:
                    largest_hand_size = hand.size
            return largest_hand_size

        def make_string_24(string):
            spaces = 24 - len(string)
            for i in range(spaces):
                string += " "
            return string

        clear()
        string = "Current Bet: {}\n".format(self.bet)
        if self.insurance:
            string += "Insured"
        string += "\n\n"
        string += make_string_24("Dealer:")
        for hand in self.hands:
            string += make_string_24("Player:")
        string += "\n"
        all_hands = [self.dealer.hand] + self.hands
        largest_hand_size = find_largest_hand_size()
        for i in range(largest_hand_size):
            for hand in all_hands:
                if hand.size <= i:
                    string += make_string_24("")
                    continue
                card = hand.backwards(i)
                if card.is_face_down:
                    string += make_string_24("*Facedown*")
                else:
                    string += make_string_24(str(card))
            string += "\n"
        for hand in all_hands:
            total, soft_ace = hand.calculate_hand()
            if total == "BUST":
                string += make_string_24("BUST")
                continue
            temp_string = "Total: {} ".format(total)
            if soft_ace:
                temp_string += "Soft Ace"
            string += make_string_24(temp_string)
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

    def __len__(self):
        count = 0
        card = self.head_card
        while card:
            count += 1
            card = card.next_card
        return count

    def backwards(self, index):
        counter = self.size-1 - index
        card = self.head_card
        while counter > 0:
            card = card.next_card
            counter -= 1
        return card

    def calculate_hand(self):
        total = 0
        soft_ace = False
        card = self.head_card
        while card:
            if card.is_face_down:
                card = card.next_card
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
                    return "BUST", 0
            card = card.next_card
        return total, soft_ace

    def calculate_total(self):
        total, soft_ace = self.calculate_hand()
        return total

    def has_soft_ace(self):
        total, soft_ace = self.calculate_hand()
        return soft_ace

    def face_down_head_card(self):
        self.head_card.is_face_down = True

    def face_up_head_card(self):
        self.head_card.is_face_down = False

class PlayerHand(Hand):
    def __init__(self, owner):
        self.head_card = None
        self.size = 0
        self.owner = owner

    def get_card(self):
        if self.calculate_total() == "BUST":
            return
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

def clear():
    os.system('clear')

def enter_casino():
    clear()
    print("Welcome to the casino!")
    print("You need chips to play Blackjack. Press enter to continue: ")
    input("")
    clear()

def enter_positive_integer(string):
    try:
        result = int(input(string))
    except ValueError:
        clear()
        print("Invalid input. Must be whole number.")
        return enter_positive_integer(string)
    if result < 0:
        clear()
        print("Invalid input. Must be positive number.")
        return enter_positive_integer(string)
    return result

def enter_YorN(string):
    result = input(string)
    while result != "Y" and result != "N" and result != "y" and result != "n":
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
while True:
    player.play_hand()
    exit = enter_YorN("Well that was fun! But gambling addiction is serious. Do you want to stop? Y or N: ")
    if exit:
        break
    clear()
    input("Alright, one more hand! Press enter to continue:")
    clear()
    player.prepare_for_next_hand()
