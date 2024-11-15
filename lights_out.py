# initialization
import matplotlib.pyplot as plt
import numpy as np
import math

# Qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.visualization import plot_histogram
from dotenv import load_dotenv
from qiskit.providers.basic_provider import BasicSimulator
from qiskit_aer import AerSimulator

# import basic plot tools
from qiskit.visualization import plot_histogram

tile = QuantumRegister(9)
flip = QuantumRegister(9)
oracle = QuantumRegister(1)
auxiliary = QuantumRegister(1)
result = ClassicalRegister(9)
# 20 qubit
qc = QuantumCircuit(tile, flip, oracle, auxiliary, result)

lights = [0, 1, 1, 1, 0, 0, 1, 1, 1]


def map_board(lights, qc, qr):
    j = 0
    for i in lights:
        if i == 1:
            qc.x(qr[j])
            j += 1
        else:
            j += 1


# Initialize
def initialize_smart(l, qc, tile):
    map_board(l, qc, tile)
    qc.h(flip[:3])
    qc.x(oracle[0])
    qc.h(oracle[0])


def flip_1(qc, flip, tile):
    # push 0
    qc.cx(flip[0], tile[0])
    qc.cx(flip[0], tile[1])
    qc.cx(flip[0], tile[3])
    # push 1
    qc.cx(flip[1], tile[0])
    qc.cx(flip[1], tile[1])
    qc.cx(flip[1], tile[2])
    qc.cx(flip[1], tile[4])
    # push 2
    qc.cx(flip[2], tile[1])
    qc.cx(flip[2], tile[2])
    qc.cx(flip[2], tile[5])


def inv_1(qc, flip, tile):
    # copy 0,1,2
    qc.cx(tile[0], flip[3])
    qc.cx(tile[1], flip[4])
    qc.cx(tile[2], flip[5])


def flip_2(qc, flip, tile):
    # apply flip[3,4,5]
    qc.cx(flip[3], tile[0])
    qc.cx(flip[3], tile[3])
    qc.cx(flip[3], tile[4])
    qc.cx(flip[3], tile[6])
    qc.cx(flip[4], tile[1])
    qc.cx(flip[4], tile[3])
    qc.cx(flip[4], tile[4])
    qc.cx(flip[4], tile[5])
    qc.cx(flip[4], tile[7])
    qc.cx(flip[5], tile[2])
    qc.cx(flip[5], tile[4])
    qc.cx(flip[5], tile[5])
    qc.cx(flip[5], tile[8])


def inv_2(qc, flip, tile1):
    # copy 3,4,5
    qc.cx(tile[3], flip[6])
    qc.cx(tile[4], flip[7])
    qc.cx(tile[5], flip[8])


def flip_3(qc, flip, tile):
    qc.cx(flip[6], tile[3])
    qc.cx(flip[6], tile[6])
    qc.cx(flip[6], tile[7])
    qc.cx(flip[7], tile[4])
    qc.cx(flip[7], tile[6])
    qc.cx(flip[7], tile[7])
    qc.cx(flip[7], tile[8])
    qc.cx(flip[8], tile[5])
    qc.cx(flip[8], tile[7])
    qc.cx(flip[8], tile[8])


def lights_out_oracle(qc, tile, oracle, auxiliary):
    qc.x(tile[6:9])
    qc.mcx(tile[6:9], oracle[0], auxiliary, mode="basic")
    qc.x(tile[6:9])


def diffusion(qc, flip):
    qc.h(flip[:3])
    qc.x(flip[:3])
    qc.h(flip[2])
    qc.ccx(flip[0], flip[1], flip[2])
    qc.h(flip[2])
    qc.x(flip[:3])
    qc.h(flip[:3])


initialize_smart(lights, qc, tile)


for i in range(2):
    flip_1(qc, flip, tile)
    inv_1(qc, flip, tile)
    flip_2(qc, flip, tile)
    inv_2(qc, flip, tile)
    flip_3(qc, flip, tile)

    lights_out_oracle(qc, tile, oracle, auxiliary)

    flip_3(qc, flip, tile)
    inv_2(qc, flip, tile)
    flip_2(qc, flip, tile)
    inv_1(qc, flip, tile)
    flip_1(qc, flip, tile)

    diffusion(qc, flip)

# Uncompute
qc.h(oracle[0])
qc.x(oracle[0])

# get the whole solution from the top row of the solution
# If you get a solution, you don't need to erase the board, so you don't need the flip_3 function.
flip_1(qc, flip, tile)
inv_1(qc, flip, tile)
flip_2(qc, flip, tile)
inv_2(qc, flip, tile)

# Measuremnt
qc.measure(flip, result)

# Make the Out put order the same as the input.
qc = qc.reverse_bits()

backend = AerSimulator()
transpiled_qc = transpile(qc, backend=backend)
result = backend.run(transpiled_qc, shots=5000).result()
counts = result.get_counts()

score_sorted = sorted(counts.items(), key=lambda x: x[1], reverse=True)
final_score = score_sorted[0:40]
print(final_score[0][0])
plot_histogram(counts)


def visualize_lights_out_grid_to_console(grid):
    """
    This function prints out the lights-out grid to the console in a nice format.

    Args:
        grid (list of int): A list of integers each representing one square in the lights-out grid and
                            whether it is on or off.
    """
    rows = []
    root = int(math.sqrt(len(grid)))

    # Chunk the list into sub lists based on each row
    chunked_grid = [grid[x : x + root] for x in range(0, len(grid), root)]

    # Iterate through each row and print as an empty or full square
    for row in chunked_grid:
        temp_list = []
        for square in row:
            if square == 1:
                temp_list.append("\u25A0")
            else:
                temp_list.append("\u25A1")
        rows.append(temp_list)

    # Print final result split by rows to make it looks nice
    print(*rows, sep="\n")
    print("\n")


def visualize_solution(grid, solution):
    """
    This function receives the lights-out grid and
    the solution to the grid that was generated from the quantum circuit.
    It then applies the solution to the grid by going through each step and flipping the squares appropriately.

    Args:
        grid (list of int): A list of integers each representing one square in the lights-out grid and
                            whether it is on or off.
        solution (string): The sequence of events to be followed to turn the whole grid off. This solution
                           is obtained from the Qiskit code.

    Returns:
        None
    """
    # Find square root of the length of the grid
    root = int(math.sqrt(len(grid)))

    # Convert solution to list of ints if it's a string
    if isinstance(solution, str):
        solution = [int(x) for x in solution]

    # Function to switch 1 -> 0 and vice versa
    def switch(square):
        if square:
            square = 0
            return square
        else:
            square = 1
            return square

    # Visualize the grid the first time before operations
    visualize_lights_out_grid_to_console(grid)

    for index, step in enumerate(solution):
        if step == 1:
            # Flip the square itself
            grid[index] = switch(grid[index])

            # Flip squares surrounding the square

            # Above
            # Check to make sure negative value doesn't wrap around the list
            if 0 <= (index - root) < len(grid):
                try:
                    grid[index - root] = switch(grid[index - root])
                except:
                    pass

            # Below
            if 0 <= (index + root) < len(grid):
                try:
                    grid[index + root] = switch(grid[index + root])
                except:
                    pass

            # Left
            # if index not in (0, 3, 6):
            if index not in tuple(range(0, len(grid), root)):
                try:
                    grid[index - 1] = switch(grid[index - 1])
                except:
                    pass
            # Right
            # if index not in (2, 5, 8):
            if index not in tuple(range(root - 1, len(grid), root)):
                try:
                    grid[index + 1] = switch(grid[index + 1])
                except:
                    pass
            visualize_lights_out_grid_to_console(grid)
    # Solution Two
    # if index in (0, 3, 6):
    #     pos = 0
    # elif index in (1, 4, 7):
    #     pos = 1
    # elif index in (2, 5, 8):
    #     pos = 2
    # # print(int(math.sqrt(len(grid))) / (index + 1))
    # if step == 1:
    #     print(sub_index, pos)
    #     print(chunked_grid[sub_index][pos])
    #     chunked_grid[sub_index][pos] = switch(chunked_grid[sub_index][pos])
    #     visualize_lights_out_grid(chunked_grid)
    # if pos == (root - 1):
    #     sub_index += 1


# visualize_lights_out_grid(lights)
if __name__ == "__main__":
    visualize_solution(lights, final_score[0][0])
