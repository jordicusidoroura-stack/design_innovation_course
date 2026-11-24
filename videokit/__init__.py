"""videokit: course session scripts (JSON) -> narrated lesson videos."""
from .engine import render, still, SCENES, BLOCKS
from .scenes_extra import EXTRA_SCENES

SCENES.update(EXTRA_SCENES)
