"""Flight data acquisition system utilities."""


import numpy as np


class ButtonEvent:
    def __init__(self, pressed, released):
        assert pressed < released
        
        self.pressed = pressed
        """The time the button was pressed."""
        
        self.released = released
        """The time the button was released."""
    
    @property
    def duration(self):
        return self.released - self.pressed

    @property
    def slice(self, t):
        return  (t >= self.pressed) & (t <= self.released)


def button_events(t, button):
    # Ensure inputs are ndarrays
    t = np.asarray(t)
    button = np.asarray(button)
    assert button.ndim == t.ndim == 1
    assert button.size == t.size
    
    # Convert button readings to logical
    threshold = 0.5*(button.min() + button.max())
    pressed = button <= threshold
    
    # Find state transitions
    state[[0, -1]] = False # Ensure we begin and end in off state
    transitions = state[1:] - state[:-1]
    
    t_pressed = t(transitions == 1)
    t_released = t(transitions == -1)
    assert t_pressed.shape == t_released.shape
    
    return [ButtonEvent(tp, tr) for (tp, tr) in zip(t_pressed, t_released)]

    
def fix_t(t):
    overruns = np.r_[0, (np.diff(t) < 0)]
    offset = np.cumsum(overruns, dtype=np.uint64) * 999000
    return t + offset

