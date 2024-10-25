import numpy as np

def get_camera_vectors(yaw, pitch):
    # Calculate forward vector
    forward = np.array([
        np.cos(np.radians(yaw)) * np.cos(np.radians(pitch)),
        np.sin(np.radians(pitch)),
        np.sin(np.radians(yaw)) * np.cos(np.radians(pitch))
    ], dtype='f4')
    
    # Normalize the forward vector
    forward = forward / np.linalg.norm(forward)
    
    # Calculate right vector (perpendicular to forward and up)
    up = np.array([0.0, 1.0, 0.0], dtype='f4')
    right = np.cross(up, forward)
    right = right / np.linalg.norm(right)
    
    # Recalculate up vector (perpendicular to forward and right)
    up = np.cross(forward, right)
    up = up / np.linalg.norm(up)
    
    return forward, right, up

# Example usage
yaw = -90.0
pitch = 0.0
forward, right, up = get_camera_vectors(yaw, pitch)

print("Forward Vector:", forward)
print("Right Vector:", right)
print("Up Vector:", up)
