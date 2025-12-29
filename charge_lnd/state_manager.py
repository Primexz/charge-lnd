import json
import time
from pathlib import Path

class StateManager:
    """Manages persistent state for strategy adjustments."""
    def __init__(self, state_file_path=None):
        if state_file_path is None:
            home = Path.home()
            state_dir = home / '.charge-lnd'
            state_dir.mkdir(parents=True, exist_ok=True)
            self.state_file = state_dir / 'flow_state.json'
        else:
            self.state_file = Path(state_file_path)
        self.state = self._load_state()

    def _load_state(self):
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_state(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=4)
        except IOError:
            pass

    def get_last_adjustment_time(self, chan_id):
        chan_id_str = str(chan_id)
        return self.state.get(chan_id_str, {}).get('last_adjustment', 0)

    def set_last_adjustment_time(self, chan_id, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        chan_id_str = str(chan_id)
        if chan_id_str not in self.state:
            self.state[chan_id_str] = {}
        self.state[chan_id_str]['last_adjustment'] = timestamp
        self._save_state()

    def should_adjust(self, chan_id, frequency_hours):
        if frequency_hours <= 0:
            return True
        last_adjustment = self.get_last_adjustment_time(chan_id)
        if last_adjustment == 0:
            return True
        current_time = time.time()
        hours_elapsed = (current_time - last_adjustment) / 3600.0
        return hours_elapsed >= frequency_hours
