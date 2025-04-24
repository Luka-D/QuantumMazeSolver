# Basic imports
import time
import numpy as np
from queue import Queue
from operator import itemgetter
from random import choice
import argparse

# Matplotlib imports
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Qiskit imports
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.providers.basic_provider import BasicSimulator
from qiskit_aer import AerSimulator

from dotenv import load_dotenv

# Imports for LED array
import board
import neopixel_spi as neopixel


load_dotenv()


maze = [
    [1, 0, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 1, 1, 0, 1, 1],
    [1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1],
]

# Dictionary that corelates the grid index to an index on the LED array (Centered in the LED array)
LED_8X8_INDICES = {
    0: 32,
    1: 39,
    2: 40,
    3: 47,
    4: 48,
    5: 55,
    6: 56,
    7: 63,
    8: 33,
    9: 38,
    10: 41,
    11: 46,
    12: 49,
    13: 54,
    14: 57,
    15: 62,
    16: 34,
    17: 37,
    18: 42,
    19: 45,
    20: 50,
    21: 53,
    22: 58,
    23: 61,
    24: 35,
    25: 36,
    26: 43,
    27: 44,
    28: 51,
    29: 52,
    30: 59,
    31: 60,
    32: 156,
    33: 155,
    34: 148,
    35: 147,
    36: 140,
    37: 139,
    38: 132,
    39: 131,
    40: 157,
    41: 154,
    42: 149,
    43: 146,
    44: 141,
    45: 138,
    46: 133,
    47: 130,
    48: 158,
    49: 153,
    50: 150,
    51: 145,
    52: 142,
    53: 137,
    54: 134,
    55: 129,
    56: 159,
    57: 152,
    58: 151,
    59: 144,
    60: 143,
    61: 136,
    62: 135,
    63: 128,
}

# Neopixel constants
NUM_PIXELS = 192
PIXEL_ORDER = neopixel.RGB

# Colors for Neopixel are in the form GRB, so switch accordingly from the standard RGB hex codes
WALL_COLOR = 0xFFFFFF  # White
FLOOR_COLOR = 0x111111  # Grey
STEP_COLOR_1 = 0x0000FF  # Blue
STEP_COLOR_2 = 0x00FF00  # Red
SOLUTION_COLOR = 0xFF0000  # Green

maze = np.array(maze)

# Thanks to Michael Gold @ https://medium.com/@msgold/using-python-to-create-and-solve-mazes-672285723c96 for the code


def BFS_alogirithm(maze, start_point, end_point):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    # Create a copy array of booleans, that we will update with where we have travelled through in the maze
    visited_array = np.zeros_like(maze, dtype=bool)
    visited_coordinate_list = []
    visited_array[start_point] = True

    # Create a queue to store our current location and possible paths
    queue = Queue()
    queue.put((start_point, []))

    while not queue.empty():
        (node, path) = queue.get()
        print(node)
        for dx, dy in directions:
            next_node = (node[0] + dx, node[1] + dy)
            if next_node == end_point:
                return path + [next_node], visited_coordinate_list
            if (
                next_node[0] >= 0
                and next_node[1] >= 0
                and next_node[0] < maze.shape[0]
                and next_node[1] < maze.shape[1]
                and maze[next_node] == 0
                and not visited_array[next_node]
            ):
                visited_array[next_node] = True
                print(path + [next_node])
                queue.put((next_node, path + [next_node]))
                visited_coordinate_list.append(next_node)
            # print(queue.queue, next_node)


def draw_maze(maze, visited_path=None, solution=None):
    fig, ax = plt.subplots(figsize=(10, 10))

    # Set the border color to white
    fig.patch.set_edgecolor("white")
    fig.patch.set_linewidth(0)

    ax.imshow(maze, cmap=plt.cm.binary, interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])

    # Prepare for path animation
    if visited_path is not None:
        (line,) = ax.plot([], [], color="red", linewidth=2)
        temp = list(map(list, zip(*visited_path)))
        x, y = temp[0], temp[1]
        print("solution", solution)
        temp2 = list(map(list, zip(*solution)))
        y2, x2 = temp2[0], temp2[1]
        (line,) = ax.plot(y, x, "ro", markersize=12)
        (line2,) = ax.plot(y, x, "go", markersize=12)
        (line3,) = ax.plot([], [], color="red", linewidth=2)

        # update is called for each path point in the maze
        def update(frame, x, y, line, line2):
            # x, y = path[frame]
            # line.set_data(
            #     *zip(*[(p[1], p[0]) for p in path[: frame + 1]])
            # )  # update the data
            if frame % 2 == 0:
                line.set_data(
                    y[: frame // 2],
                    x[: frame // 2],
                )
                line2.set_data(
                    y[: frame // 2],
                    x[: frame // 2],
                )
            else:
                line.set_data(
                    y[: (frame // 2) + 1],
                    x[: (frame // 2) + 1],
                )
            return [line, line2]

        def update2(frame, x2, y2, line):
            line.set_data(x2[:frame], y2[:frame])
            return (line,)

        def init():
            line3.set_data([], [])
            return (line3,)

        # First animation to show BFS algorithm steps
        ani = animation.FuncAnimation(
            fig,
            update,
            frames=2 * len(visited_path) + 1,
            fargs=[x, y, line, line2],
            blit=True,
            repeat=False,
            interval=250,
        )

        # Second animation to show the line path solution
        ani2 = animation.FuncAnimation(
            fig,
            update2,
            frames=len(solution),
            init_func=init,
            fargs=[x2, y2, line3],
            blit=True,
            repeat=False,
            interval=250,
        )

    # Draw entry and exit arrows
    ax.arrow(1, 0, 0, 0.4, fc="green", ec="green", head_width=0.3, head_length=0.3)
    ax.arrow(
        1,
        7,
        0,
        0.4,
        fc="blue",
        ec="blue",
        head_width=0.3,
        head_length=0.3,
    )
    plt.show()


def visualize_solution(maze, visited_coordinate_list, solution, args):
    """
    This function receives the lights-out grid and
    the solution to the grid that was generated from the quantum circuit.
    It then applies the solution to the grid by going through each step and flipping the squares appropriately.

    Args:
        grid (list of int): A list of integers each representing one square in the lights-out grid and
                            whether it is on or off.
        solution (string): The sequence of events to be followed to turn the whole grid off. This solution
                           is obtained from the Qiskit code.
        console (bool): Determines whether the lights out grid is also printed to the console during each
                        step.
        delay (float): The delay between iteration steps.
        brightness (float): The brightness of the LED pixels.
    Returns:
        None
    """
    # Set all command line args
    console = args.console
    delay = args.delay
    brightness = args.brightness

    # Neopixel initialization
    spi = board.SPI()

    neopixel_array = neopixel.NeoPixel_SPI(
        spi,
        NUM_PIXELS,
        pixel_order=PIXEL_ORDER,
        brightness=brightness,
        auto_write=False,
    )

    # Display Initial Maze
    print(maze)
    for index, value in enumerate(maze.flatten()):
        # Get the corresponding index position on the LED array
        LED_index = LED_8X8_INDICES[index]
        if value:
            color = WALL_COLOR
        else:
            color = FLOOR_COLOR
        neopixel_array[LED_index] = color
    neopixel_array.show()
    time.sleep(delay)

    # Display BSF Solution Process
    for coord in visited_coordinate_list:
        print(coord)
        x, y = coord[0], coord[1]
        index = (x * 8) + y
        print(index)
        LED_index = LED_8X8_INDICES[index]

        # Display the new step in blue, then keep it on the board in red
        neopixel_array[LED_index] = STEP_COLOR_1
        neopixel_array.show()
        time.sleep(delay / 2)

        neopixel_array[LED_index] = STEP_COLOR_2
        neopixel_array.show()
        time.sleep(delay / 2)
    time.sleep(delay)

    # Display Maze Solution
    for coord in solution:
        x, y = coord[0], coord[1]
        index = (x * 8) + y
        print(index)
        LED_index = LED_8X8_INDICES[index]
        color = SOLUTION_COLOR
        neopixel_array[LED_index] = color
        neopixel_array.show()
    time.sleep(delay)

    # Clear Maze
    # neopixel_array.fill(0)
    # neopixel_array.show()


# Not sure if this is needed now that we use matplotlib, will probably remove
def print_maze(maze):
    row_num = 0
    maze_str = ""
    for row in maze:
        row_str = ""
        if row_num == 0 or row_num == np.shape(maze)[0] - 1:
            is_top_or_bottom = True
        else:
            is_top_or_bottom = False
        for value in row:
            if value and is_top_or_bottom:
                row_str += "-"
            elif value:
                row_str += "|"
            else:
                row_str += " "
        row_str += "\n"
        maze_str += row_str
        row_num += 1
    print(maze_str)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--console",
        help="Displays the maze solution to the console",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--delay",
        help="Sets the delay (in seconds) between iteration steps for the LED array and console",
        required=False,
        type=float,
        default=1.0,
    )
    parser.add_argument(
        "-b",
        "--brightness",
        help="Sets the brightness of LEDs, between 0.0 and 1.0",
        required=False,
        type=float,
        default=1.0,
    )
    return parser.parse_args()


def main(*args, **kwargs):
    # Qiskit init
    # if os.getenv("Qiskit_API_Token"):
    #     print("API Token Successfully Loaded")
    # else:
    #     raise Exception(
    #         "Qiskit API Token not found. Please verify it is correctly declared in your .env file."
    #     )

    # try:
    #     print("Establishing connection")
    #     service = QiskitRuntimeService(
    #         channel="ibm_quantum",
    #         token=os.getenv("Qiskit_API_Token"),
    #     )
    # except Exception as e:
    #     print(e)
    # backend = service.backend(name="ibm_brisbane")
    # print(backend.num_qubits)

    args = parse_arguments()
    try:
        print("Starting Quantum Maze Solver!")
        print("Finding Solution to Maze...")
        # Create optimal solution and save the procedure used for the solution using the BFS Algorithm
        start_point = (0, 1)
        end_point = (7, 1)
        solution, visited_coordinate_list = BFS_alogirithm(maze, start_point, end_point)
        print("Maze Solution Found!")

        # Add the start and endpoints to the solution coordinates
        solution.insert(0, start_point)
        solution.append(end_point)

        # Add the start and endpoints to the visited coordinates
        visited_coordinate_list.insert(0, start_point)
        visited_coordinate_list.append(end_point)
        print(visited_coordinate_list)

        # Order the list of coordinates(tuples) by row so that it doesn't jump around as much
        # visited_coordinate_list = sorted(visited_coordinate_list, key=itemgetter(0))
        print(visited_coordinate_list)

        if args.console:
            # Display the procedure on a plot of the maze
            draw_maze(maze, visited_coordinate_list, solution)

        # Display to LEDs
        print("Displaying BFS Process to LEDs...")
        visualize_solution(maze, visited_coordinate_list, solution, args)

    except Exception as e:
        print("An error occured: ", e)


if __name__ == "__main__":
    main()
