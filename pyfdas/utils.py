"""Flight data acquisition system utilities."""


import numpy as np


class ButtonEvent:
    def __init__(self, pressed, released):
        assert pressed < released
        
        self.pressed = pressed
        """The time the button was pressed."""
        
        self.released = released
        """The time the button was released."""

        self.middle = 0.5 * (self.pressed + self.released)
        """The time in the middle of the event."""
    
    @property
    def duration(self):
        return self.released - self.pressed
    
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
    state = button <= threshold
    
    # Find state transitions
    state[[0, -1]] = False # Ensure we begin and end in off state
    transitions = np.ediff1d(np.asarray(state, dtype=int), to_end=0)
    
    t_pressed = t[transitions == 1]
    t_released = t[transitions == -1]
    assert t_pressed.shape == t_released.shape
    
    return [ButtonEvent(tp, tr) for (tp, tr) in zip(t_pressed, t_released)]


def plot_events(t, x, events):
    from matplotlib import pyplot
    
    pyplot.plot(t, x, 'b-')
    pyplot.hold(True)
    for number, e in enumerate(events):
        i = e.slice(t)
        xe = x[i]
        te = t[i]
        pyplot.plot(te, xe, 'g.-')
        pyplot.text(e.middle, xe[0], number, color='black')
    pyplot.hold(False)
