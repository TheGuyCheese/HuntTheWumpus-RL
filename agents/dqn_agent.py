import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
import random

class DQNNetwork(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQNNetwork, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, output_dim)
        )
    
    def forward(self, x):
        return self.network(x)

class DQNAgent:
    def __init__(self, state_dim, action_dim, learning_rate=0.001, gamma=0.99,
                 epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.995,
                 memory_size=10000, batch_size=64):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        
        # Neural Networks
        self.policy_net = DQNNetwork(state_dim, action_dim)
        self.target_net = DQNNetwork(state_dim, action_dim)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        self.memory = deque(maxlen=memory_size)
        
        # Training metrics
        self.losses = []
        self.rewards = []
        self.episode_lengths = []
        
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state, training=True):
        if training and random.random() < self.epsilon:
            return random.randrange(self.action_dim)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.policy_net(state_tensor)
            return q_values.argmax().item()
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        
        try:
            batch = random.sample(self.memory, self.batch_size)
            states, actions, rewards, next_states, dones = zip(*batch)
            
            states = torch.FloatTensor(np.array(states))
            actions = torch.LongTensor(actions)
            rewards = torch.FloatTensor(rewards)
            next_states = torch.FloatTensor(np.array(next_states))
            dones = torch.FloatTensor(dones)
            
            # Get current Q values
            current_q_values = self.policy_net(states)
            current_q_values = current_q_values.gather(1, actions.unsqueeze(1))
            
            # Get next Q values
            with torch.no_grad():
                next_q_values = self.target_net(next_states).max(1)[0].detach()
            
            # Compute target Q values
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
            
            # Compute loss
            loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
            
            # Optimize the model
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping to prevent exploding gradients
            torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            self.losses.append(loss.item())
            
            # Decay epsilon
            self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
            
        except Exception as e:
            print(f"Error in replay: {str(e)}")
            return
    
    def update_target_network(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def preprocess_state(self, state_dict):
        """Convert dictionary observation to flat array"""
        # Convert each component to float32 and flatten
        state_components = [
            state_dict['grid_size'].flatten(),
            state_dict['player_pos'].flatten(),
            state_dict['wumpus_positions'].flatten(),
            state_dict['pit_positions'].flatten(),
            state_dict['gold_position'].flatten(),
            state_dict['has_gold'].flatten(),
            state_dict['visited_cells'].flatten()
        ]
        return np.concatenate(state_components).astype(np.float32)
    
    def save(self, path):
        """Save the model"""
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_metrics': {
                'losses': self.losses,
                'rewards': self.rewards,
                'episode_lengths': self.episode_lengths
            }
        }, path)
    
    def load(self, path):
        """Load the model"""
        checkpoint = torch.load(path)
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        
        # Load training metrics
        metrics = checkpoint['training_metrics']
        self.losses = metrics['losses']
        self.rewards = metrics['rewards']
        self.episode_lengths = metrics['episode_lengths']
