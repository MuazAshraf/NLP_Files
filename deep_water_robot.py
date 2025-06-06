import numpy as np
import heapq
import random
import matplotlib.pyplot as plt

# --- 1. Diffusion Model ---
def apply_diffusion(grid, D=0.1, iterations=50):
    new_grid = grid.copy()
    for _ in range(iterations):
        # Diffusion step: apply diffusion over the grid
        for i in range(1, grid.shape[0] - 1):
            for j in range(1, grid.shape[1] - 1):
                new_grid[i, j] = grid[i, j] + D * (np.sum(grid[i-1:i+2, j-1:j+2]) - 8 * grid[i, j])
    return new_grid

# --- 2. A* Algorithm for Pathfinding ---
def astar(start, goal, grid):
    # Directions for movement (up, down, left, right)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    def cost(node, grid):
        # Use the diffusion model to get environmental costs
        return grid[node[0], node[1]]

    open_list = []
    heapq.heappush(open_list, (0 + heuristic(start, goal), 0, start))  # (f, g, position)
    came_from = {}
    g_score = {start: 0}

    while open_list:
        _, current_g, current = heapq.heappop(open_list)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
                tentative_g = current_g + 1  # Assume cost between adjacent nodes is 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal) + cost(neighbor, grid)
                    heapq.heappush(open_list, (f_score, tentative_g, neighbor))
                    came_from[neighbor] = current

    return None  # No path found

# --- 3. Q-Learning for Reinforcement Learning ---
class QLearningAgent:
    def __init__(self, grid_size, actions, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.grid_size = grid_size
        self.actions = actions  # Possible movements (up, down, left, right)
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.q_table = np.zeros((grid_size, grid_size, len(actions)))  # Q-values table

    def get_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            # Explore: random action
            return random.choice(range(len(self.actions)))
        else:
            # Exploit: best action based on Q-values
            return np.argmax(self.q_table[state[0], state[1]])

    def update_q_table(self, state, action, reward, next_state):
        max_next_q = np.max(self.q_table[next_state[0], next_state[1]])  # Best Q-value for next state
        current_q = self.q_table[state[0], state[1], action]
        self.q_table[state[0], state[1], action] = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)

# --- Main Execution ---
def run_simulation():
    # Set grid size
    grid_size = 50
    grid = np.zeros((grid_size, grid_size))  # Empty grid, modify for obstacles and environment

    # Set start and goal positions
    start = (10, 10)
    goal = (40, 40)

    # Initialize the diffusion model
    for _ in range(10):  # Apply diffusion for 10 iterations
        grid = apply_diffusion(grid, D=0.1, iterations=5)

    # --- A* Pathfinding ---
    path = astar(start, goal, grid)
    
    # Visualize the grid and path from A* algorithm
    if path:
        path_grid = np.zeros_like(grid)
        for (x, y) in path:
            path_grid[x, y] = 1  # Mark the path
        plt.imshow(path_grid, cmap='Blues')
        plt.colorbar()
        plt.show()

    # --- Q-Learning Agent for Navigation ---
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    agent = QLearningAgent(grid_size, actions)

    # Simulate the agent moving from start to goal
    agent_position = start
    steps = 0
    while agent_position != goal and steps < 1000:
        action_idx = agent.get_action(agent_position)
        action = actions[action_idx]
        next_position = (agent_position[0] + action[0], agent_position[1] + action[1])

        # Check if the next position is within bounds
        if 0 <= next_position[0] < grid_size and 0 <= next_position[1] < grid_size:
            reward = -1  # Cost of movement
            if next_position == goal:
                reward = 100  # Reward for reaching the goal
            agent.update_q_table(agent_position, action_idx, reward, next_position)
            agent_position = next_position
        steps += 1

    print(f"Agent reached goal in {steps} steps.")

run_simulation()
