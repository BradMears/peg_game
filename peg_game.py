#!/usr/bin/env python3
"""Generate all solutions to the peg game - 15 holes & 14 pegs."""

# This implementation is a pure python solution without any optimization.
# It can be used as a baseline for comparison with other implementations.

# The allowed moves for each position are a tuple consisting of the
# position being jumped over and the position being jumped to. The
# from position is the index in the array.
ALLOWED_MOVES = (
    ((1, 3), (2, 5)),  # 0
    ((3, 6), (4, 8)),  # 1
    ((4, 7), (5, 9)),  # 2
    ((1, 0), (4, 5), (7, 12), (6, 10)),  # 3
    ((7, 11), (8, 13)),  # 4
    ((2, 0), (4, 3), (8, 12), (9, 14)),  # 5
    ((3, 1), (7, 8)),  # 6
    ((4, 2), (8, 9)),  # 7
    ((4, 1), (7, 6)),  # 8
    ((5, 2), (8, 7)),  # 9
    ((6, 3), (11, 12)),  # 10
    ((7, 4), (12, 13)),  # 11
    ((7, 3), (8, 5), (11, 10), (13, 14)),  # 12
    ((8, 4), (12, 11)),  # 13
    ((9, 5), (13, 12)),  # 14
)

## Global variables to track statistics about the games played

# Histogram of starting positions that lead to a single peg left
starting_positions = [0] * 15 

# Histogram of # remaining pegs at the end of each game
remaining_count = [0] * 14

# Histogram of the last remaining peg for each game that ends with a single peg
last_remaining_peg = [0] * 15

lowest_weight = 10000  # global variable to track the lowest weight found
winning_moves = []  # global variable to track the moves that produced the lowest weight

print_count = 0  # global variable to limit the number of full solutions printed

winners = []  # global variable to track the moves that produced a single peg left

openers = {}  # global variable to track the stats of all opening moves

def calculate_weight(moves):
    """Calculate the weight of a set of moves."""
    weight = 0
    for pos, over, to in moves:
        weight += pos + over + to
    return weight

def validate(moves):
    """Given a set of moves, make sure they are all legal and end with no more possible moves."""
    assert len(moves) > 0
    assert len(moves) < 14

    # Create the starting board by finding the 'to' element of the first move
    # and setting that position to blank
    empty_spot = moves[0][2]
    board = [empty_spot != x for x in range(15)]

    # For each move in the game, verify that it is legal and then apply it to the board
    for pos, over, to in moves:
        assert board[pos]
        assert board[over]
        assert not board[to]
        board[pos] = False
        board[over] = False
        board[to] = True

    # Check every position to see that no more valid moves exist
    for pos in range(15):
        for over, to in ALLOWED_MOVES[pos]:
            if board[pos] and board[over]:
                assert board[to]

def move(board, moves, pos, over, to):
    """Record a move and then kick off the remainder of the game."""
    global print_count
    global lowest_weight, winning_moves

    board[pos] = False
    board[over] = False
    board[to] = True
    moves.append([pos, over, to])
    game_over = play(board, moves)  # Keep playing with the updated board
    if game_over:  # that's the end of this game
        peg_count = sum(board)
        remaining_count[peg_count] += 1

        # The opening_moves dictionary uses the first two moves as the key and stores both the total
        # number of times that opening move was used and the number of times it ended in a winning game.
        #opening_move = (peg_count, f'{moves[0]}-{moves[1]}')
        opening_move = f'{moves[0]}-{moves[1]}'
        total_times, winning_times = openers.get(opening_move, (0,0))
        total_times += 1
        if peg_count == 1:
            winning_times += 1
        openers[opening_move] = (total_times, winning_times)

        # Collect statistics on the last remaining hole and starting positions that lead to a single peg left
        if peg_count == 1 :
            assert moves[-1][2] == board.index(True)  # The last move's 'to' position should be the only peg left
            last_remaining_peg[board.index(True)] += 1
            starting_positions[moves[0][0]] += 1  # track which starting positions lead to a single peg left
            winners.append(moves.copy())
            weight = calculate_weight(moves)

            # The most common starting position that leads to a single peg left is 3 and the most common
            # ending position is 3, so we only track the lowest weight for that combination.
            if moves[0][2] == 3 and board[3] and weight < lowest_weight:
                lowest_weight = weight
                winning_moves = moves.copy()

        # Print the pessimal games
        if len(moves) < 5 :
            print('Final:', (peg_count, moves))

        # This was used during development and debug to validate that the moves
        # were all legal and that the game ended with no more valid moves.
        # That logic is solid now and this validation is no longer needed, but 
        # it can be uncommented to verify that the moves are valid.
        #validate(moves)


def play(board, moves):
    """Start from the existing board, walk through all available moves."""
    # This is recursive and doesn't unwind until no more valid moves remain.
    game_over = True
    for pos, _ in enumerate(board):  # for every spot on the board
        if board[pos]:  # if it has a peg
            for over, to in ALLOWED_MOVES[
                pos
            ]:  # loop over all allowed moves from that position
                if board[over] and not board[to]:  # If a move is open
                    move(board.copy(), moves.copy(), pos, over, to)
                    game_over = False

    return game_over


def main():
    """Entry point."""
    unique_starting_positions = [
        0,
        1,
        3,
        4,
    ]  # all other positions are rotations or mirrors of these
    #unique_starting_positions = range(15)  # Uncomment this line to test all starting positions

    for pos in unique_starting_positions:
        board = [pos != x for x in range(15)] # Populates the board with True for pegs and False for the empty starting position
        moves = []
        play(board, moves)

    # Print the histogram
    print(f'Lowest weight: {lowest_weight}, Winning moves: {winning_moves}')
    for idx, val in enumerate(remaining_count):
        print(idx, val)

    print('Last remaining peg counts:', last_remaining_peg)
    print('Starting position counts:', starting_positions)

    # #winners = sorted(winners)
    # opening_moves = {}
    # with open('winners.csv', 'w') as f:
    #     for winner in sorted(winners):
    #         #the_opening_move = (winner[0], winner[1])
    #         the_opening_move = f'{winner[0]}-{winner[1]}'
    #         opening_moves[the_opening_move] = opening_moves.get(the_opening_move, 0) + 1
    #         for m in winner:
    #             f.write(f'{m[0]}-{m[1]}-{m[2]}, ')
    #         f.write(f'\n')

    # print('Opening moves counts:', opening_moves)
    print('')
    for key, value in openers.items():
        print(f"{key}: {value}  ({value[1]/value[0]:.2%})")

if __name__ == "__main__":
    main()
