import os
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime

def plot_training_results(results_file='results/training_results.json', save_dir='plots'):
    """Plot training results from saved JSON file"""
    # Create plots directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    # Load results from JSON file
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define colors for different algorithms
    colors = ['#2ecc71', '#e74c3c', '#3498db', '#f1c40f']
    
    # Plot training rewards
    plt.figure(figsize=(12, 6))
    
    # Plot all algorithms
    color_idx = 0
    for algo, data in results.items():
        if 'episode_rewards' in data:
            label = algo.replace('_', ' ').upper()
            plt.plot(data['episode_rewards'], 
                    label=label, 
                    color=colors[color_idx], 
                    linewidth=2,
                    alpha=0.8)
            color_idx = (color_idx + 1) % len(colors)
    
    plt.title('Training Rewards Across Algorithms', fontsize=14, pad=20)
    plt.xlabel('Episode', fontsize=12)
    plt.ylabel('Reward', fontsize=12)
    plt.legend(fontsize=10, loc='upper left')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f'training_rewards_{timestamp}.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot evaluation comparison
    plt.figure(figsize=(10, 6))
    
    algorithms = []
    eval_means = []
    eval_stds = []
    
    for algo, data in results.items():
        if 'eval_rewards' in data:
            algorithms.append(algo.replace('_', ' ').upper())
            eval_means.append(np.mean(data['eval_rewards']))
            eval_stds.append(np.std(data['eval_rewards']))
    
    if algorithms:
        bars = plt.bar(range(len(algorithms)), eval_means, 
                      yerr=eval_stds, 
                      capsize=5,
                      color=colors[:len(algorithms)],
                      alpha=0.8)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom')
        
        plt.title('Final Performance Comparison', fontsize=14, pad=20)
        plt.ylabel('Mean Evaluation Reward', fontsize=12)
        plt.xticks(range(len(algorithms)), algorithms, rotation=45, ha='right')
        plt.grid(True, axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f'performance_comparison_{timestamp}.png'), dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    plot_training_results()
