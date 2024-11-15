import time
import os
from queue import Queue
from operator import itemgetter
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dotenv import load_dotenv
import qiskit
from qiskit_ibm_runtime import QiskitRuntimeService

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
        # (line,) = ax.plot([], [], color="red", linewidth=2)
        temp = list(map(list, zip(*visited_path)))
        x, y = temp[0], temp[1]
        print("solution", solution)
        temp2 = list(map(list, zip(*solution)))
        y2, x2 = temp2[0], temp2[1]
        # (line,) = ax.plot(y, x, "ro", markersize=12)
        # (line2,) = ax.plot(y, x, "go", markersize=12)
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
        # ani = animation.FuncAnimation(
        #     fig,
        #     update,
        #     frames=2 * len(visited_path) + 1,
        #     fargs=[x, y, line, line2],
        #     blit=True,
        #     repeat=False,
        #     interval=250,
        # )

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
    # ax.arrow(1, 0, 0, 0.4, fc="green", ec="green", head_width=0.3, head_length=0.3)
    # ax.arrow(
    #     1,
    #     7,
    #     0,
    #     0.4,
    #     fc="blue",
    #     ec="blue",
    #     head_width=0.3,
    #     head_length=0.3,
    # )
    plt.show()


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


if __name__ == "__main__":
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

    # Create optimal solution and save the procedure used for the solution using the BFS Algorithm
    start_point = (0, 1)
    end_point = (7, 1)
    solution, visited_coordinate_list = BFS_alogirithm(maze, start_point, end_point)

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

    # Display the procedure on a plot of the maze
    draw_maze(maze, visited_coordinate_list, solution)
