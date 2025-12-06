# Kinematics and Dynamics

## Overview

Kinematics and dynamics are fundamental to understanding robot motion. Kinematics studies motion without considering forces, while dynamics analyzes the forces causing motion. Mastering these concepts is essential for robot control and trajectory planning.

## Learning Objectives

By the end of this chapter, you will:
- Understand forward and inverse kinematics
- Apply homogeneous transformations
- Calculate robot velocities using Jacobians
- Understand robot dynamics and equations of motion
- Implement basic kinematic solutions in code

## Kinematics: The Geometry of Motion

### Forward Kinematics (FK)

**Definition**: Computing end-effector position/orientation from joint angles.

**Given**: Joint angles θ₁, θ₂, ..., θₙ  
**Find**: End-effector pose (position + orientation)

#### 2-DOF Planar Arm Example

```python
import numpy as np

def forward_kinematics_2dof(theta1, theta2, L1, L2):
    """
    Forward kinematics for 2-link planar arm
    
    Args:
        theta1: Joint 1 angle (radians)
        theta2: Joint 2 angle (radians)
        L1: Link 1 length
        L2: Link 2 length
    
    Returns:
        x, y: End-effector position
    """
    x = L1 * np.cos(theta1) + L2 * np.cos(theta1 + theta2)
    y = L1 * np.sin(theta1) + L2 * np.sin(theta1 + theta2)
    
    return x, y

# Example usage
L1, L2 = 0.5, 0.3  # meters
theta1 = np.radians(30)  # 30 degrees
theta2 = np.radians(45)  # 45 degrees

x, y = forward_kinematics_2dof(theta1, theta2, L1, L2)
print(f"End-effector position: ({x:.3f}, {y:.3f})")
```

### Inverse Kinematics (IK)

**Definition**: Computing joint angles from desired end-effector pose.

**Given**: End-effector pose (x, y, z, orientation)  
**Find**: Joint angles θ₁, θ₂, ..., θₙ

**Challenge**: Often multiple solutions or no solution exists.

#### 2-DOF Planar Arm - Analytical Solution

```python
def inverse_kinematics_2dof(x, y, L1, L2):
    """
    Inverse kinematics for 2-link planar arm (elbow-down solution)
    
    Args:
        x, y: Desired end-effector position
        L1, L2: Link lengths
    
    Returns:
        theta1, theta2: Joint angles (radians)
        valid: Boolean indicating if solution exists
    """
    # Check if point is reachable
    distance = np.sqrt(x**2 + y**2)
    if distance > (L1 + L2) or distance < abs(L1 - L2):
        return None, None, False
    
    # Law of cosines for theta2
    cos_theta2 = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)
    
    # Clamp to valid range to handle numerical errors
    cos_theta2 = np.clip(cos_theta2, -1.0, 1.0)
    
    theta2 = np.arccos(cos_theta2)  # Elbow-down solution
    # theta2 = -np.arccos(cos_theta2)  # Elbow-up solution
    
    # Calculate theta1
    k1 = L1 + L2 * np.cos(theta2)
    k2 = L2 * np.sin(theta2)
    
    theta1 = np.arctan2(y, x) - np.arctan2(k2, k1)
    
    return theta1, theta2, True

# Example
x_desired, y_desired = 0.6, 0.4
theta1, theta2, valid = inverse_kinematics_2dof(x_desired, y_desired, L1, L2)

if valid:
    print(f"Joint angles: θ₁={np.degrees(theta1):.1f}°, θ₂={np.degrees(theta2):.1f}°")
    
    # Verify solution
    x_fk, y_fk = forward_kinematics_2dof(theta1, theta2, L1, L2)
    error = np.sqrt((x_fk - x_desired)**2 + (y_fk - y_desired)**2)
    print(f"Verification error: {error:.6f} m")
else:
    print("Target position unreachable!")
```

## Homogeneous Transformations

Homogeneous transformations combine rotation and translation in a single 4×4 matrix.

### Transformation Matrix Structure

```
T = [R | p]  =  [r₁₁  r₁₂  r₁₃ | pₓ]
    [0 | 1]     [r₂₁  r₂₂  r₂₃ | pᵧ]
                [r₃₁  r₃₂  r₃₃ | pᵧ]
                [ 0    0    0  | 1 ]

R = 3×3 rotation matrix
p = 3×1 position vector
```

### Basic Transformations

```python
def rotation_z(theta):
    """Rotation about Z-axis"""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]
    ])

def translation(dx, dy, dz):
    """Pure translation"""
    return np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0,  1]
    ])

def transform_point(T, point):
    """Transform a 3D point using homogeneous transformation"""
    # Convert to homogeneous coordinates
    p_homo = np.append(point, 1)
    # Apply transformation
    p_transformed = T @ p_homo
    # Return 3D point
    return p_transformed[:3]
```

### Denavit-Hartenberg (DH) Parameters

Standardized method for describing robot kinematics using 4 parameters per link:

- **a**: Link length
- **α**: Link twist
- **d**: Link offset
- **θ**: Joint angle

```python
def dh_transform(a, alpha, d, theta):
    """
    Create transformation matrix from DH parameters
    """
    c_t, s_t = np.cos(theta), np.sin(theta)
    c_a, s_a = np.cos(alpha), np.sin(alpha)
    
    return np.array([
        [c_t,    -s_t*c_a,  s_t*s_a,   a*c_t],
        [s_t,     c_t*c_a, -c_t*s_a,   a*s_t],
        [0,       s_a,      c_a,       d    ],
        [0,       0,        0,         1    ]
    ])
```

## Differential Kinematics

Relates joint velocities to end-effector velocities.

### Jacobian Matrix

The Jacobian J maps joint velocities to end-effector velocities:

```
ẋ = J(θ) θ̇

where:
ẋ = end-effector velocity (linear + angular)
θ̇ = joint velocities
J = Jacobian matrix (6×n for n joints)
```

### 2-DOF Planar Arm Jacobian

```python
def jacobian_2dof(theta1, theta2, L1, L2):
    """
    Compute Jacobian for 2-link planar arm
    
    Returns 2×2 Jacobian relating joint velocities to end-effector velocity
    """
    s1 = np.sin(theta1)
    c1 = np.cos(theta1)
    s12 = np.sin(theta1 + theta2)
    c12 = np.cos(theta1 + theta2)
    
    J = np.array([
        [-L1*s1 - L2*s12, -L2*s12],
        [ L1*c1 + L2*c12,  L2*c12]
    ])
    
    return J

# Example: Calculate end-effector velocity
theta1, theta2 = np.radians([30, 45])
theta_dot = np.array([0.5, 0.3])  # rad/s

J = jacobian_2dof(theta1, theta2, L1, L2)
x_dot = J @ theta_dot

print(f"End-effector velocity: vₓ={x_dot[0]:.3f} m/s, vᵧ={x_dot[1]:.3f} m/s")
```

### Singularities

**Definition**: Configurations where the Jacobian loses rank (becomes singular).

**Consequences**:
- Loss of mobility in certain directions
- Infinite joint velocities required
- Control instability

**Detection**: Check if det(J) ≈ 0

```python
def detect_singularity(J, threshold=1e-3):
    """Check if robot is near a singularity"""
    det_J = np.linalg.det(J)
    return abs(det_J) < threshold

# Check for singularity
is_singular = detect_singularity(J)
if is_singular:
    print("Warning: Robot near singularity!")
```

## Robot Dynamics

Dynamics studies the relationship between forces/torques and motion.

### Equations of Motion

The dynamics of a robot manipulator can be expressed as:

```
τ = M(θ)θ̈ + C(θ,θ̇)θ̇ + G(θ) + F(θ̇)

where:
τ = joint torques
M(θ) = inertia matrix
C(θ,θ̇) = Coriolis and centrifugal terms
G(θ) = gravity terms
F(θ̇) = friction terms
```

### Lagrangian Formulation

```
L = K - P

where:
K = kinetic energy
P = potential energy

Equations of motion:
d/dt(∂L/∂θ̇) - ∂L/∂θ = τ
```

### Simple Example: Single Pendulum

```python
def pendulum_dynamics(theta, theta_dot, torque, m, L, g=9.81):
    """
    Dynamics of a simple pendulum
    
    Args:
        theta: angle from vertical (radians)
        theta_dot: angular velocity (rad/s)
        torque: applied torque (N⋅m)
        m: mass (kg)
        L: length (m)
        g: gravity (m/s²)
    
    Returns:
        theta_ddot: angular acceleration (rad/s²)
    """
    I = m * L**2  # Moment of inertia
    theta_ddot = (torque - m * g * L * np.sin(theta)) / I
    
    return theta_ddot

# Simulate pendulum motion
def simulate_pendulum(theta0, duration, dt=0.01):
    """Simple Euler integration"""
    time = np.arange(0, duration, dt)
    theta = np.zeros_like(time)
    theta_dot = np.zeros_like(time)
    
    theta[0] = theta0
    m, L = 1.0, 1.0  # 1kg, 1m
    
    for i in range(len(time) - 1):
        torque = 0  # Free swing
        theta_ddot = pendulum_dynamics(theta[i], theta_dot[i], torque, m, L)
        
        theta_dot[i+1] = theta_dot[i] + theta_ddot * dt
        theta[i+1] = theta[i] + theta_dot[i+1] * dt
    
    return time, theta

# Run simulation
time, angles = simulate_pendulum(theta0=np.radians(30), duration=5.0)
print(f"Simulated {len(time)} timesteps")
```

## Trajectory Planning

Planning smooth paths between configurations.

### Point-to-Point Motion

**Cubic Polynomial Trajectory**:

```python
def cubic_trajectory(q0, qf, t0, tf, t):
    """
    Generate cubic polynomial trajectory
    
    Args:
        q0: initial position
        qf: final position
        t0: start time
        tf: end time
        t: current time
    
    Returns:
        q, q_dot, q_ddot: position, velocity, acceleration
    """
    T = tf - t0
    s = (t - t0) / T  # Normalized time [0, 1]
    
    # Cubic polynomial: q(s) = a₀ + a₁s + a₂s² + a₃s³
    # Boundary conditions: q(0)=q0, q(1)=qf, q̇(0)=0, q̇(1)=0
    
    q = q0 + (qf - q0) * (3*s**2 - 2*s**3)
    q_dot = (qf - q0) * (6*s - 6*s**2) / T
    q_ddot = (qf - q0) * (6 - 12*s) / T**2
    
    return q, q_dot, q_ddot

# Generate trajectory
t = np.linspace(0, 2, 100)  # 2 seconds
positions = []
velocities = []

for ti in t:
    q, q_dot, _ = cubic_trajectory(q0=0, qf=np.pi/2, t0=0, tf=2, t=ti)
    positions.append(q)
    velocities.append(q_dot)

print(f"Generated trajectory with {len(positions)} waypoints")
```

### Velocity Profiles

**Trapezoidal Velocity Profile**:
- Constant acceleration phase
- Constant velocity phase
- Constant deceleration phase

Used for smooth, predictable motion.

## Numerical Methods for IK

When analytical solutions don't exist, use numerical methods.

### Newton-Raphson Method

```python
def ik_newton_raphson(target, theta_init, L1, L2, max_iter=100, tol=1e-6):
    """
    Solve IK using Newton-Raphson iteration
    
    Args:
        target: Desired (x, y) position
        theta_init: Initial guess for joint angles
        max_iter: Maximum iterations
        tol: Convergence tolerance
    
    Returns:
        theta: Solution joint angles
        converged: Boolean success flag
    """
    theta = np.array(theta_init)
    
    for i in range(max_iter):
        # Forward kinematics
        x, y = forward_kinematics_2dof(theta[0], theta[1], L1, L2)
        error = np.array([target[0] - x, target[1] - y])
        
        # Check convergence
        if np.linalg.norm(error) < tol:
            return theta, True
        
        # Compute Jacobian
        J = jacobian_2dof(theta[0], theta[1], L1, L2)
        
        # Newton-Raphson update: θ_new = θ_old + J⁻¹ * error
        try:
            delta_theta = np.linalg.solve(J, error)
            theta += delta_theta
        except np.linalg.LinAlgError:
            print("Singular Jacobian encountered!")
            return theta, False
    
    return theta, False

# Example usage
target_pos = (0.5, 0.5)
initial_guess = (0.5, 0.5)  # radians
solution, success = ik_newton_raphson(target_pos, initial_guess, L1, L2)

if success:
    print(f"IK Solution: θ₁={np.degrees(solution[0]):.1f}°, θ₂={np.degrees(solution[1]):.1f}°")
```

## Key Takeaways

1. Forward kinematics computes end-effector pose from joint angles
2. Inverse kinematics is often more complex with multiple or no solutions
3. Homogeneous transformations unify rotation and translation
4. The Jacobian relates joint and end-effector velocities
5. Robot dynamics involve inertia, Coriolis, gravity, and friction forces
6. Trajectory planning ensures smooth, controlled motion
7. Numerical methods solve complex IK problems

## Further Reading

1. **"Robot Modeling and Control"** by Mark W. Spong - Chapter 3 (Forward Kinematics) and Chapter 4 (Inverse Kinematics)
2. **"Modern Robotics"** by Kevin Lynch and Frank Park - Available free online
3. **"Introduction to Robotics"** by John J. Craig - Chapters 2-6
4. **Peter Corke's Robotics Toolbox**: https://petercorke.com/toolboxes/robotics-toolbox/

## Exercises

1. Derive the forward kinematics for a 3-DOF planar robot arm
2. Implement inverse kinematics for a 3-DOF robot and handle multiple solutions
3. Calculate the Jacobian for a SCARA robot configuration
4. Simulate a 2-link robot following a circular trajectory
5. Analyze singularities for different robot configurations

---

**Previous**: [← Robotics Fundamentals](./02-robotics-fundamentals.md) | **Next**: [Control Systems →](./05-control-systems.md)