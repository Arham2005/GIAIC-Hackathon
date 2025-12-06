# Machine Learning for Robotics

## Overview

Machine learning enables robots to learn from experience, adapt to new situations, and improve performance over time. This chapter explores how ML techniques are applied to robotic perception, control, and decision-making.

## Learning Objectives

After this chapter, you will:
- Understand key ML paradigms for robotics
- Apply supervised learning to robot perception
- Implement reinforcement learning for control
- Use imitation learning for skill acquisition
- Understand the challenges of learning in physical systems

## Why Machine Learning for Robotics?

Traditional robotics relies on explicitly programmed behaviors. ML offers:

1. **Adaptability**: Learn from changing environments
2. **Generalization**: Handle novel situations
3. **Automation**: Reduce manual engineering
4. **Performance**: Optimize through experience
5. **Scalability**: Learn from massive datasets

### Challenges

- **Sample efficiency**: Physical experiments are slow/expensive
- **Safety**: Learning must avoid dangerous behaviors
- **Sim-to-real gap**: Simulations don't perfectly match reality
- **Partial observability**: Sensors provide incomplete information
- **Continuous state/action spaces**: High-dimensional problems

## Machine Learning Paradigms

### 1. Supervised Learning

**Definition**: Learn from labeled input-output pairs.

**Applications**:
- Object detection
- Pose estimation
- Grasp quality prediction
- Failure prediction

#### Example: Object Classification

```python
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

# Simulated robot sensor data (features) and object labels
def generate_robot_data(n_samples=1000):
    """Generate synthetic sensor data"""
    X = []
    y = []
    
    for _ in range(n_samples):
        if np.random.rand() > 0.5:
            # Object type 0: cube (features: size, weight, texture)
            features = [np.random.uniform(0.05, 0.15),  # size
                       np.random.uniform(0.1, 0.5),     # weight
                       np.random.uniform(0, 0.3)]       # texture roughness
            label = 0
        else:
            # Object type 1: sphere
            features = [np.random.uniform(0.03, 0.1),
                       np.random.uniform(0.05, 0.3),
                       np.random.uniform(0.3, 1.0)]
            label = 1
        
        X.append(features)
        y.append(label)
    
    return np.array(X), np.array(y)

# Train object classifier
X, y = generate_robot_data(1000)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

clf = MLPClassifier(hidden_layer_sizes=(10, 10), max_iter=1000)
clf.fit(X_train, y_train)

accuracy = clf.score(X_test, y_test)
print(f"Object classification accuracy: {accuracy:.2%}")

# Predict object type from sensor reading
new_object = [[0.08, 0.25, 0.15]]  # size, weight, texture
prediction = clf.predict(new_object)
print(f"Predicted object type: {prediction[0]}")
```

### 2. Unsupervised Learning

**Definition**: Discover patterns in unlabeled data.

**Applications**:
- Anomaly detection
- Clustering similar objects
- Dimensionality reduction
- Feature learning

#### Example: Clustering Robot States

```python
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Robot state data: [joint1_angle, joint2_angle, end_effector_force]
robot_states = np.random.randn(300, 3)
robot_states[:100] += [0, 0, 0]     # Cluster 1: normal operation
robot_states[100:200] += [2, 2, 0]  # Cluster 2: extended reach
robot_states[200:] += [0, 0, 5]     # Cluster 3: high force

# Cluster states
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(robot_states)

print(f"Found {len(np.unique(clusters))} distinct operational modes")
print(f"Cluster centers:\n{kmeans.cluster_centers_}")
```

### 3. Reinforcement Learning (RL)

**Definition**: Learn through trial and error using reward signals.

**Key Concepts**:
- **Agent**: The robot
- **Environment**: The physical world
- **State** (s): Current situation
- **Action** (a): What the robot does
- **Reward** (r): Feedback signal
- **Policy** (π): Mapping from states to actions

**Goal**: Maximize cumulative reward

```
Total Reward = Σ γᵗ · r_t

where γ = discount factor (0 < γ ≤ 1)
```

#### Example: Q-Learning for Robot Navigation

```python
class GridWorldRobot:
    """Simple grid world for robot navigation"""
    def __init__(self, size=5):
        self.size = size
        self.goal = (size-1, size-1)
        self.reset()
    
    def reset(self):
        self.position = (0, 0)
        return self.position
    
    def step(self, action):
        # Actions: 0=up, 1=right, 2=down, 3=left
        moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        new_pos = (
            self.position[0] + moves[action][0],
            self.position[1] + moves[action][1]
        )
        
        # Check boundaries
        if (0 <= new_pos[0] < self.size and 0 <= new_pos[1] < self.size):
            self.position = new_pos
        
        # Reward
        if self.position == self.goal:
            reward = 10
            done = True
        else:
            reward = -0.1  # Small penalty for each step
            done = False
        
        return self.position, reward, done

# Q-Learning algorithm
def q_learning(env, episodes=1000, alpha=0.1, gamma=0.95, epsilon=0.1):
    """Train robot using Q-learning"""
    Q = {}  # Q-table: {(state, action): value}
    
    for episode in range(episodes):
        state = env.reset()
        done = False
        
        while not done:
            # Epsilon-greedy action selection
            if np.random.rand() < epsilon:
                action = np.random.randint(4)  # Explore
            else:
                # Exploit: choose best action
                q_values = [Q.get((state, a), 0) for a in range(4)]
                action = np.argmax(q_values)
            
            # Take action
            next_state, reward, done = env.step(action)
            
            # Q-learning update
            old_q = Q.get((state, action), 0)
            next_max_q = max([Q.get((next_state, a), 0) for a in range(4)])
            
            Q[(state, action)] = old_q + alpha * (reward + gamma * next_max_q - old_q)
            
            state = next_state
    
    return Q

# Train the robot
env = GridWorldRobot(size=5)
Q_table = q_learning(env, episodes=1000)

print(f"Learned Q-values for {len(Q_table)} state-action pairs")

# Test learned policy
state = env.reset()
path = [state]
for _ in range(20):
    q_values = [Q_table.get((state, a), 0) for a in range(4)]
    action = np.argmax(q_values)
    state, reward, done = env.step(action)
    path.append(state)
    if done:
        break

print(f"Robot path: {path}")
```

### 4. Imitation Learning (Learning from Demonstration)

**Definition**: Learn by observing expert demonstrations.

**Advantages**:
- Faster than RL (no trial-and-error)
- Safer (expert provides safe examples)
- Better initialization for RL

**Methods**:
- Behavioral cloning (supervised learning)
- Inverse reinforcement learning
- DAgger (Dataset Aggregation)

#### Example: Behavioral Cloning

```python
from sklearn.linear_model import LinearRegression

# Collect expert demonstrations
def collect_expert_data(n_demos=100):
    """Simulate expert robot controller"""
    states = []
    actions = []
    
    for _ in range(n_demos):
        # State: [position_error, velocity]
        state = np.random.randn(2)
        
        # Expert policy: PD controller
        Kp, Kd = 2.0, 0.5
        action = -Kp * state[0] - Kd * state[1]
        
        states.append(state)
        actions.append(action)
    
    return np.array(states), np.array(actions).reshape(-1, 1)

# Learn from expert
states, actions = collect_expert_data(500)
policy = LinearRegression()
policy.fit(states, actions)

print(f"Learned policy coefficients: {policy.coef_}")
print(f"Policy intercept: {policy.intercept_}")

# Test learned policy
test_state = np.array([[0.5, 0.2]])  # [error, velocity]
predicted_action = policy.predict(test_state)
print(f"For state {test_state[0]}, learned action: {predicted_action[0][0]:.3f}")
```

## Deep Learning for Robot Perception

### Convolutional Neural Networks (CNNs)

Used for vision tasks:
- Object detection
- Semantic segmentation
- Depth estimation
- Visual servoing

#### Example: Simple CNN for Grasp Quality Prediction

```python
import torch
import torch.nn as nn

class GraspQualityNet(nn.Module):
    """CNN to predict grasp success from RGB-D images"""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(4, 32, kernel_size=3, padding=1)  # 4 channels: RGB-D
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 16 * 16, 128)
        self.fc2 = nn.Linear(128, 1)  # Output: grasp quality score
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(-1, 64 * 16 * 16)
        x = self.relu(self.fc1(x))
        x = self.sigmoid(self.fc2(x))  # Score between 0 and 1
        return x

# Initialize model
model = GraspQualityNet()
print(f"Model has {sum(p.numel() for p in model.parameters())} parameters")

# Example prediction
dummy_rgbd = torch.randn(1, 4, 64, 64)  # Batch of 1, 64x64 RGB-D image
quality_score = model(dummy_rgbd)
print(f"Predicted grasp quality: {quality_score.item():.3f}")
```

### Transfer Learning

Leverage pre-trained models for robotic tasks:

```python
import torchvision.models as models

# Load pre-trained ResNet
resnet = models.resnet18(pretrained=True)

# Freeze early layers
for param in resnet.parameters():
    param.requires_grad = False

# Replace final layer for robot-specific task
num_features = resnet.fc.in_features
resnet.fc = nn.Linear(num_features, 10)  # 10 object classes

print("Transfer learning model ready for fine-tuning")
```

## End-to-End Learning

Learn direct mapping from sensors to actions.

### Advantages
- Minimal feature engineering
- Can discover non-obvious patterns
- Unified representation

### Challenges
- Requires lots of data
- Black-box behavior
- Safety concerns

### Example: Vision-Based Control

```python
class VisionBasedController(nn.Module):
    """End-to-end model: image -> robot actions"""
    def __init__(self, action_dim=7):  # 7 DOF robot
        super().__init__()
        # Vision encoder
        self.conv1 = nn.Conv2d(3, 32, 5, stride=2)
        self.conv2 = nn.Conv2d(32, 64, 3, stride=2)
        self.conv3 = nn.Conv2d(64, 128, 3, stride=2)
        
        # Action decoder
        self.fc1 = nn.Linear(128 * 6 * 6, 256)
        self.fc2 = nn.Linear(256, action_dim)
        
        self.relu = nn.ReLU()
    
    def forward(self, image):
        # Encode image
        x = self.relu(self.conv1(image))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        
        # Flatten and decode to actions
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        actions = self.fc2(x)
        
        return actions

controller = VisionBasedController(action_dim=7)
test_image = torch.randn(1, 3, 224, 224)
actions = controller(test_image)
print(f"Predicted actions: {actions.shape}")
```

## Sim-to-Real Transfer

Training in simulation, deploying on real robots.

### Domain Randomization

Vary simulation parameters to improve real-world generalization:

```python
def randomize_simulation():
    """Randomize simulation parameters"""
    params = {
        'lighting': np.random.uniform(0.5, 1.5),
        'friction': np.random.uniform(0.3, 0.9),
        'object_mass': np.random.uniform(0.05, 0.2),
        'camera_noise': np.random.uniform(0, 0.05),
        'actuator_noise': np.random.uniform(0, 0.02)
    }
    return params

# Train with randomized environments
for episode in range(1000):
    sim_params = randomize_simulation()
    # ... run episode with these parameters
```

### Domain Adaptation

Techniques to bridge sim-real gap:
- Feature matching
- Adversarial training
- Style transfer

## Active Learning

Robot decides what data to collect for maximum learning benefit.

```python
def uncertainty_sampling(model, unlabeled_data, n_samples=10):
    """Select most uncertain samples for labeling"""
    predictions = model.predict_proba(unlabeled_data)
    
    # Calculate uncertainty (entropy)
    entropy = -np.sum(predictions * np.log(predictions + 1e-10), axis=1)
    
    # Select top uncertain samples
    uncertain_indices = np.argsort(entropy)[-n_samples:]
    
    return uncertain_indices

# Example usage
# uncertain_samples = unlabeled_data[uncertain_indices]
# Ask human or execute in real world for labels
```

## Key Takeaways

1. ML enables robots to learn from experience and adapt
2. Supervised learning works well for perception tasks
3. Reinforcement learning discovers optimal behaviors through trial-and-error
4. Imitation learning accelerates training by using expert demonstrations
5. Deep learning excels at vision-based tasks
6. Sim-to-real transfer reduces real-world data requirements
7. Safety and sample efficiency remain key challenges

## Further Reading

1. **"Deep Learning for Robot Perception and Cognition"** - Various papers from RSS, ICRA, CoRL
2. **"Reinforcement Learning: An Introduction"** by Sutton and Barto
3. **OpenAI Robotics Research**: https://openai.com/research/#robotics
4. **Google DeepMind Robotics**: https://deepmind.google/discover/blog/
5. **PyTorch Robotics Tutorials**: https://pytorch.org/tutorials/

## Exercises

1. Implement a neural network to predict robot joint torques from sensor data
2. Train a Q-learning agent to navigate a maze
3. Compare behavioral cloning vs RL for a simple manipulation task
4. Implement domain randomization for a simulated grasping task
5. Design an active learning strategy for collecting robot training data

---

**Previous**: [← Perception and Vision](./06-perception-and-vision.md) | **Next**: [Reinforcement Learning →](./08-reinforcement-learning.md)