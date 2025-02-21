# Hunt the Wumpus with Reinforcement Learning

This project implements an adaptive version of the classic Hunt the Wumpus game using various Reinforcement Learning algorithms. The game features dynamic difficulty adjustment based on player performance and can be trained using multiple RL approaches.

## Project Structure

```
.
├── agents/
│   └── dqn_agent.py         # Custom DQN implementation
├── env/
│   └── wumpus_env.py        # Gymnasium environment for Wumpus World
├── assets/                   # Game assets (images, sounds)
├── plots/                   # Training visualization plots
├── results/                 # Training results and metrics
├── main.py                 # Main game implementation
├── train.py               # Training script for RL agents
└── requirements.txt       # Project dependencies
```

## Features

1. Dynamic Difficulty Adjustment:
   - Grid size adapts based on player performance
   - Wumpus and pit frequencies adjust automatically
   - Reward scaling based on difficulty level

2. Multiple RL Algorithms:
   - Custom DQN implementation
   - Stable-Baselines3 implementations (PPO, A2C, DQN)
   - Performance comparison across algorithms

3. Performance Visualization:
   - Training rewards plots
   - Algorithm comparison graphs
   - Performance metrics visualization

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. To play the game:
```bash
python main.py
```

2. To train the RL agents:
```bash
python train.py
```

## Training Details

The project implements several RL algorithms:

1. Custom DQN:
   - Deep Q-Network with experience replay
   - Epsilon-greedy exploration
   - Target network for stability

2. Stable-Baselines3 Algorithms:
   - Proximal Policy Optimization (PPO)
   - Advantage Actor-Critic (A2C)
   - Deep Q-Network (DQN)

## Dynamic Difficulty Adjustment

The game automatically adjusts its difficulty based on player performance:

- Success rate > 70%: Increases difficulty
  - Larger grid size
  - More Wumpus and pits
  - Higher gold rewards

- Success rate < 30%: Decreases difficulty
  - Smaller grid size
  - Fewer Wumpus and pits
  - Lower gold rewards

## Model Architectures

### 1. Custom DQN
Our custom DQN implementation includes several improvements over the basic DQN algorithm:

- **Network Architecture**:
  - Input Layer: State dimension (grid_size + player_pos + entities + visited_cells)
  - Hidden Layers: 2 fully connected layers with 128 and 64 units
  - ReLU activation between layers
  - Output Layer: 4 units (one for each action)

- **Key Improvements**:
  - Experience Replay Buffer with capacity of 10000 transitions
  - Target Network for stable training
  - Epsilon-greedy exploration with decay
  - Gradient clipping to prevent exploding gradients
  - Batch normalization for better training stability
  - Prioritized experience replay for better sample efficiency

### 2. Stable-Baselines3 PPO (Proximal Policy Optimization)
- **Architecture**:
  - Actor Network:
    - Shared feature extractor (MultiInputPolicy)
    - Policy head: 2 fully connected layers (64 units each)
    - Value head: 2 fully connected layers (64 units each)
  - Advantages:
    - Better sample efficiency
    - More stable training
    - Clip parameter to limit policy updates

### 3. Stable-Baselines3 A2C (Advantage Actor-Critic)
- **Architecture**:
  - Actor-Critic Network:
    - Shared feature extractor (MultiInputPolicy)
    - Policy network: 2 fully connected layers (64 units)
    - Value network: 2 fully connected layers (64 units)
  - Features:
    - Parallel environment training
    - N-step returns for better credit assignment
    - Entropy regularization for exploration

### 4. Stable-Baselines3 DQN
- **Architecture**:
  - Q-Network:
    - MultiInputPolicy for handling dictionary observations
    - 3 fully connected layers (256, 128, 64 units)
    - Dueling network architecture
  - Features:
    - Double Q-learning
    - Priority replay buffer
    - Target network updates

## Training Parameters
- Episodes: 100 for Custom DQN
- Timesteps: 10000 for SB3 algorithms
- Evaluation Episodes: 10
- Max Steps per Episode: 200

## Custom DQN Improvements Detail

1. **Experience Replay**:
   - Stores (state, action, reward, next_state, done) tuples
   - Random sampling reduces correlation between consecutive samples
   - Buffer size: 10000 transitions
   - Batch size: 32

2. **Target Network**:
   - Separate network for generating target Q-values
   - Updated every 5 episodes
   - Helps reduce overestimation of Q-values

3. **Exploration Strategy**:
   - Epsilon-greedy with decay
   - Initial epsilon: 1.0
   - Final epsilon: 0.01
   - Decay rate: 0.995

4. **Training Stability**:
   - Gradient clipping at 1.0
   - Batch normalization in hidden layers
   - Learning rate: 0.001
   - Discount factor (gamma): 0.99

5. **Architecture Improvements**:
   - State preprocessing for better feature representation
   - ReLU activation for better gradient flow
   - Proper weight initialization
   - Dropout layers for regularization

## Results

Training results are saved in the `plots/` directory:
- Learning curves for each algorithm
- Performance comparison boxplots
- Evaluation metrics

## Contributing

This is a research project. Please ensure any contributions:
1. Follow the existing code structure
2. Include appropriate documentation
3. Add relevant tests
4. Update the README as needed

## License

MIT License
