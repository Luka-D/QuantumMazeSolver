# Basic imports
import matplotlib.pyplot as plt
import numpy as np
import math
import time

# Qiskit imports
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.visualization import plot_histogram
from dotenv import load_dotenv
from qiskit.providers.basic_provider import BasicSimulator
from qiskit_aer import AerSimulator

# import basic plot tools
from qiskit.visualization import plot_histogram

# Imports for LED array
# import board
# import neopixel_spi as neopixel

# Array containing the initial lights out grid values
lights = [0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0]

# Dictionary that corelates the grid index to an index on the LED array (Centered in the LED array)
LED_array_indices = {
    0: 12,
    1: 13,
    2: 14,
    3: 22,
    4: 23,
    5: 24,
    6: 32,
    7: 33,
    8: 34,
}

# Delay before showing the next iteration
delay = 1


def compute_quantum_solution(lights):
    """
    This function creates a quantum circuit and uses it to compute the solution to the light-sout grid.

    Args:
        lights (list of int): A list of integers each representing one square in the lights-out grid and
                              whether it is on or off.
    Returns:
        quantum_solution (str): A string representing each square in the grid.
                                If a square is 1, it must be pressed to solved the grid.
    """
    # Initialize quantum circuit board
    tile = QuantumRegister(16)
    flip = QuantumRegister(16)
    oracle = QuantumRegister(1)
    auxiliary = QuantumRegister(15)
    result = ClassicalRegister(16)

    qc = QuantumCircuit(tile, flip, oracle, auxiliary, result)

    def map_board(lights, qc, qr):
        j = 0
        for i in lights:
            if i == 1:
                qc.x(qr[j])
                j += 1
            else:
                j += 1

    # Initialize
    def initialize():
        map_board(lights, qc, tile)

        qc.h(flip[0:17])
        qc.x(oracle[0])
        qc.h(oracle[0])

    # Subroutine for oracle
    # Calculate what the light state will be after pressing each solution candidate.
    def flip_tile(qc, flip, tile):
        qc.cx(flip[0], tile[0])
        qc.cx(flip[0], tile[1])
        qc.cx(flip[0], tile[4])
        qc.cx(flip[1], tile[0])
        qc.cx(flip[1], tile[1])
        qc.cx(flip[1], tile[2])
        qc.cx(flip[1], tile[5])
        qc.cx(flip[2], tile[1])
        qc.cx(flip[2], tile[2])
        qc.cx(flip[2], tile[6])
        qc.cx(flip[2], tile[3])
        qc.cx(flip[3], tile[2])
        qc.cx(flip[3], tile[3])
        qc.cx(flip[3], tile[7])
        qc.cx(flip[4], tile[0])
        qc.cx(flip[4], tile[4])
        qc.cx(flip[4], tile[5])
        qc.cx(flip[4], tile[8])
        qc.cx(flip[5], tile[1])
        qc.cx(flip[5], tile[4])
        qc.cx(flip[5], tile[5])
        qc.cx(flip[5], tile[6])
        qc.cx(flip[5], tile[9])
        qc.cx(flip[6], tile[2])
        qc.cx(flip[6], tile[5])
        qc.cx(flip[6], tile[6])
        qc.cx(flip[6], tile[7])
        qc.cx(flip[6], tile[10])
        qc.cx(flip[7], tile[3])
        qc.cx(flip[7], tile[6])
        qc.cx(flip[7], tile[7])
        qc.cx(flip[7], tile[11])
        qc.cx(flip[8], tile[4])
        qc.cx(flip[8], tile[8])
        qc.cx(flip[8], tile[9])
        qc.cx(flip[8], tile[12])
        qc.cx(flip[9], tile[5])
        qc.cx(flip[9], tile[8])
        qc.cx(flip[9], tile[9])
        qc.cx(flip[9], tile[10])
        qc.cx(flip[9], tile[13])
        qc.cx(flip[10], tile[6])
        qc.cx(flip[10], tile[9])
        qc.cx(flip[10], tile[10])
        qc.cx(flip[10], tile[11])
        qc.cx(flip[10], tile[14])
        qc.cx(flip[11], tile[7])
        qc.cx(flip[11], tile[10])
        qc.cx(flip[11], tile[11])
        qc.cx(flip[11], tile[15])
        qc.cx(flip[12], tile[8])
        qc.cx(flip[12], tile[12])
        qc.cx(flip[12], tile[13])
        qc.cx(flip[13], tile[9])
        qc.cx(flip[13], tile[12])
        qc.cx(flip[13], tile[13])
        qc.cx(flip[13], tile[14])
        qc.cx(flip[14], tile[10])
        qc.cx(flip[14], tile[13])
        qc.cx(flip[14], tile[14])
        qc.cx(flip[14], tile[15])
        qc.cx(flip[15], tile[11])
        qc.cx(flip[15], tile[14])
        qc.cx(flip[15], tile[15])

    def lights_out_oracle(qc, tile, oracle, auxiliary):
        qc.x(tile[0:16])
        qc.mcx(tile[0:16], oracle[0], auxiliary[0:14], mode="basic")
        qc.x(tile[0:16])

    def diffusion(qc, flip, auxiliary):
        qc.h(flip)
        qc.x(flip)
        qc.h(flip[15])
        qc.mcx(flip[0:15], flip[15], auxiliary[0:14], mode="basic")
        qc.h(flip[15])
        qc.x(flip)
        qc.h(flip)

    initialize()

    for i in range(17):
        # oracle
        flip_tile(qc, flip, tile)
        lights_out_oracle(qc, tile, oracle, auxiliary)

        # Diffusion
        flip_tile(qc, flip, tile)
        diffusion(qc, flip, auxiliary)

    print("uncompute")
    # Uncompute
    qc.h(oracle[0])
    qc.x(oracle[0])

    # Measurment
    qc.measure(flip, result)

    # Make the Out put order the same as the input.
    qc = qc.reverse_bits()

    print("Backend simulation")
    backend = AerSimulator(method="matrix_product_state")
    transpiled_qc = transpile(qc, backend=backend)
    result = backend.run(transpiled_qc, shots=5000).result()
    counts = result.get_counts()

    score_sorted = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    final_score = score_sorted[0:40]
    print(final_score[0][0])
    plot_histogram(counts)
    quantum_solution = final_score[0][0]
    return quantum_solution


def visualize_lights_out_grid_to_console(grid):
    """
    This function prints out the lights-out grid to the console in a nice format.

    Args:
        grid (list of int): A list of integers each representing one square in the lights-out grid and
                            whether it is on or off.
    Returns:
        None
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


def visualize_lights_out_grid_to_LED(grid):
    """
    This function shows the lights-out grid on the LED arrray.

    Args:
        grid (list of int): A list of integers each representing one square in the lights-out grid and
                            whether it is on or off.
    Returns:
        None
    """

    # For later
    # NUM_PIXELS = 192
    # PIXEL_ORDER = neopixel.RGB

    # spi = board.SPI()

    # pixels = neopixel.NeoPixel_SPI(
    #     spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False
    # )

    color = 0x800080  # Other colors: 0x7F00FF for Violet, 0xBF40BF for Bright Purple

    # Iterate through each row and print as an empty or full square
    for index, square in enumerate(grid):
        LED_array_index = LED_array_indices[index]
        if square == 1:
            print("Full", LED_array_index, color)
            # pixels[LED_array_index] = color
        else:
            print("Empty", LED_array_index)

    # pixels.show()
    # Sleep so that the display doesn't change too fast
    time.sleep(delay)


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


# visualize_lights_out_grid(lights)
if __name__ == "__main__":
    quantum_solution = compute_quantum_solution(lights)
    print(quantum_solution)
    visualize_solution(lights, quantum_solution)
