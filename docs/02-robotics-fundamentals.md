# Robotics Fundamentals

## Overview

This chapter introduces the foundational concepts of robotics, including robot anatomy, degrees of freedom, coordinate systems, and basic mechanical principles that enable robots to move and interact with their environment.

## Learning Objectives

After completing this chapter, you will be able to:
- Understand robot anatomy and classification
- Explain degrees of freedom and workspace
- Work with coordinate systems and transformations
- Identify different types of robot configurations
- Understand basic mechanical design principles

## What is a Robot?

A robot is a programmable mechanical system capable of:
1. **Sensing** its environment
2. **Processing** information
3. **Acting** on the environment
4. **Repeating** tasks with precision

### ISO Definition
According to ISO 8373, a robot is an "automatically controlled, reprogrammable, multipurpose manipulator programmable in three or more axes."

## Robot Anatomy

### Main Components

```
Robot System = Mechanical Structure + Sensors + Actuators + Controller + Software
```

#### 1. Mechanical Structure
- **Links**: Rigid body segments
- **Joints**: Connections allowing relative motion
- **End Effector**: Tool at the end (gripper, welding torch, etc.)
- **Base**: Foundation providing stability

#### 2. Actuators
- **Electric Motors**: Most common, precise control
- **Hydraulic**: High force applications
- **Pneumatic**: Fast, low-cost applications

#### 3. Sensors
- **Position Sensors**: Encoders, potentiometers
- **Force/Torque Sensors**: Measure interaction forces
- **Vision Sensors**: Cameras, depth sensors
- **Tactile Sensors**: Touch-sensitive surfaces

#### 4. Control System
- **Controller**: Computer processing sensor data
- **Power Supply**: Energy source
- **Communication**: Interfaces with other systems

## Degrees of Freedom (DOF)

**Degrees of Freedom** represent the number of independent ways a robot can move.

### Examples

**1-DOF**: Simple gripper (open/close)
**2-DOF**: Pan-tilt camera mount
**3-DOF**: Cartesian robot (X, Y, Z motion)
**6-DOF**: Industrial robot arm (full spatial positioning)
**7-DOF+**: Redundant robots (more flexibility)

### Human Arm Analogy
- Shoulder: 3 DOF (flexion/extension, abduction/adduction, rotation)
- Elbow: 1 DOF (flexion/extension)
- Wrist: 3 DOF (pronation/supination, flexion/extension, radial/ulnar deviation)
- **Total**: 7 DOF per arm

## Coordinate Systems

### Types of Coordinate Systems

#### 1. Cartesian (Rectangular)
```
Point P = (x, y, z)
```
- Most intuitive for humans
- Used in CNC machines, 3D printers

#### 2. Cylindrical
```
Point P = (r, θ, z)
r = radius
θ = angle
z = height
```
- Common in warehouse robots
- SCARA robots use this

#### 3. Spherical
```
Point P = (ρ, θ, φ)
ρ = radius
θ = azimuth angle
φ = elevation angle
```
- Used in radar systems
- Some robotic arms

### Coordinate Transformations

Transforming between coordinate systems is fundamental:

```python
import numpy as np

def cartesian_to_cylindrical(x, y, z):
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    return r, theta, z

def cylindrical_to_cartesian(r, theta, z):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y, z
```

## Robot Configurations

### 1. Cartesian (Gantry) Robot
- **DOF**: 3 (X, Y, Z)
- **Workspace**: Rectangular box
- **Applications**: 3D printing, CNC machines, pick-and-place
- **Advantages**: Simple kinematics, high precision
- **Disadvantages**: Large footprint, limited flexibility

### 2. Cylindrical Robot
- **DOF**: 3 (r, θ, z)
- **Workspace**: Cylindrical volume
- **Applications**: Assembly, machine tending
- **Advantages**: Good reach, simple control
- **Disadvantages**: Limited workspace shape

### 3. Spherical (Polar) Robot
- **DOF**: 3 (ρ, θ, φ)
- **Workspace**: Partial sphere
- **Applications**: Welding, material handling
- **Advantages**: Large workspace relative to size
- **Disadvantages**: Complex kinematics

### 4. SCARA (Selective Compliance Assembly Robot Arm)
- **DOF**: 4 (2 rotational + 1 prismatic + 1 rotational)
- **Workspace**: Cylindrical with horizontal motion
- **Applications**: Electronic assembly, pick-and-place
- **Advantages**: High speed, good for horizontal assembly
- **Disadvantages**: Limited vertical reach

### 5. Articulated (Anthropomorphic)
- **DOF**: 6+ (all rotational joints)
- **Workspace**: Complex, approximately spherical
- **Applications**: Welding, painting, assembly
- **Advantages**: Most flexible, human-like reach
- **Disadvantages**: Complex kinematics, expensive

### 6. Delta (Parallel) Robot
- **DOF**: 3-4
- **Workspace**: Inverted cone
- **Applications**: High-speed picking, packaging
- **Advantages**: Extremely fast, accurate
- **Disadvantages**: Limited workspace, complex design

## Workspace Analysis

### Reachable Workspace
The set of all points a robot's end effector can reach.

### Dexterous Workspace
Points reachable with arbitrary orientation of the end effector.

### Workspace Volume Calculation

For a simple 2-DOF planar arm:
```python
def calculate_workspace_2dof(L1, L2):
    """
    Calculate workspace for 2-link planar arm
    L1, L2: Link lengths
    """
    R_max = L1 + L2  # Maximum reach
    R_min = abs(L1 - L2)  # Minimum reach (if links can fold)
    
    # Workspace is an annulus (ring)
    area = np.pi * (R_max**2 - R_min**2)
    return area, R_min, R_max

# Example
L1, L2 = 0.5, 0.3  # meters
area, r_min, r_max = calculate_workspace_2dof(L1, L2)
print(f"Workspace area: {area:.2f} m²")
print(f"Reach: {r_min:.2f} m to {r_max:.2f} m")
```

## Joint Types

### Revolute (R)
- Rotational motion around an axis
- Range typically: 0° to 360° (or limited)
- Symbol: ⟲

### Prismatic (P)
- Linear sliding motion
- Range: typically 0 to several meters
- Symbol: ⇅

### Common Joint Sequences
- **RRR**: 3-DOF articulated arm
- **RPR**: SCARA-type configuration
- **PPP**: Cartesian robot
- **RRRRRR**: 6-DOF industrial robot

## Robot Specifications

### Key Performance Metrics

#### 1. Payload
Maximum weight the robot can manipulate
- Typical range: 1 kg to 1000+ kg
- Affects motor sizing and structure

#### 2. Reach
Maximum distance from base to end effector
- Horizontal reach
- Vertical reach
- Example: UR10 has 1300mm reach

#### 3. Repeatability
Ability to return to same position
- Typical: ±0.02mm to ±0.5mm
- Critical for precision tasks
- Better than absolute accuracy

#### 4. Speed
Maximum velocity of end effector
- Linear speed: m/s
- Angular speed: °/s or rad/s
- Example: Delta robots can reach 10+ m/s

#### 5. Accuracy
Difference between commanded and actual position
- Typically 1-5mm for industrial robots
- Affected by calibration, load, wear

## Mechanical Design Principles

### 1. Structural Rigidity
```
Deflection = Force × Length³ / (E × I)

E = Young's modulus (material stiffness)
I = Moment of inertia (cross-section shape)
```

**Design guidelines:**
- Use high-strength materials (aluminum, carbon fiber)
- Optimize cross-sections (hollow tubes, I-beams)
- Minimize link lengths
- Add structural bracing

### 2. Weight Optimization
Reducing weight improves:
- Energy efficiency
- Speed
- Payload capacity
- Lifespan (less wear)

**Techniques:**
- Material selection (aluminum vs steel)
- Hollow structures
- Topology optimization
- Composite materials

### 3. Gear Ratios
```
Gear Ratio = Output Torque / Input Torque = Input Speed / Output Speed
```

**Common configurations:**
- Direct drive: No gears, high speed, low torque
- 100:1 ratio: High torque, low speed
- Harmonic drives: High ratio, low backlash

### 4. Backlash Minimization
Backlash = play or clearance in mechanical systems

**Reduction methods:**
- Precision gears
- Preloaded bearings
- Direct drive motors
- Strain wave gearing

## Safety Considerations

### Mechanical Safety

1. **Emergency Stops**: Accessible buttons
2. **Soft Limits**: Software-defined boundaries
3. **Hard Limits**: Physical limit switches
4. **Force Limiting**: Torque sensors detect collisions
5. **Speed Reduction**: Slower motion near humans

### Collaborative Robots (Cobots)
Designed to work safely alongside humans:
- Force-limited joints
- Rounded edges
- Compliant materials
- Safety-rated sensors

## Key Takeaways

1. Robots consist of links, joints, actuators, sensors, and controllers
2. Degrees of Freedom determine robot capabilities and workspace
3. Different robot configurations suit different applications
4. Coordinate systems enable precise positioning
5. Mechanical design affects performance, precision, and safety
6. Understanding fundamentals is essential for advanced robotics

## Further Reading

1. **"Introduction to Robotics: Mechanics and Control"** by John J. Craig
2. **"Robot Modeling and Control"** by Mark W. Spong, Seth Hutchinson, and M. Vidyasagar
3. **"Robotics: Modelling, Planning and Control"** by Bruno Siciliano and Lorenzo Sciavicco
4. **Universal Robots Academy**: https://academy.universal-robots.com/

## Exercises

1. Calculate the workspace volume for a 3-DOF cylindrical robot with specific dimensions
2. Compare and contrast Cartesian vs Articulated robot configurations for a pick-and-place application
3. Design a simple 2-DOF robotic arm on paper, specifying joint types and expected workspace
4. Research and analyze the specifications of three commercial industrial robots

---

**Previous**: [← Introduction to Physical AI](./01-introduction-to-physical-ai.md) | **Next**: [Kinematics and Dynamics →](./04-kinematics-and-dynamics.md)