# Example RL agent (stable-baselines3) to tune aggregation weights or hyperparameters
from stable_baselines3 import PPO
from stable_baselines3.common.envs import DummyVecEnv
import gymnasium as gym
import numpy as np




class SimpleOptEnv(gym.Env):
# A toy environment where agent chooses aggregation weight and receives reward based on 'accuracy'
metadata = {"render.modes": ["human"]}


def __init__(self):
super(SimpleOptEnv, self).__init__()
# Action: continuous weight between 0 and 1
self.action_space = gym.spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
# Observation: last accuracy and round number
self.observation_space = gym.spaces.Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32)
self.round = 0
self.last_acc = 0.5


def reset(self):
self.round = 0
self.last_acc = 0.5
return np.array([self.last_acc, float(self.round)], dtype=np.float32)


def step(self, action):
weight = float(action[0])
# Toy dynamic: reward = improvement over last_acc scaled by weight
simulated_acc = min(1.0, self.last_acc + 0.05 * (weight - 0.5) + np.random.randn() * 0.01)
reward = simulated_acc - self.last_acc
self.last_acc = simulated_acc
self.round += 1
done = self.round >= 20
obs = np.array([self.last_acc, float(self.round)], dtype=np.float32)
return obs, reward, done, False, {}




def train_rl_agent(save_path: str = "models/ppo_agent.zip"):
env = DummyVecEnv([lambda: SimpleOptEnv()])
model = PPO("MlpPolicy", env, verbose=0)
model.learn(total_timesteps=2000)
model.save(save_path)
return save_path