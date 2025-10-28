from typing import Dict


class VoiceAssistantUsecase:
    """State helpers for controlling voice assistant behaviour."""

    def set_wake_word_enabled(self, enabled: bool) -> Dict[str, Dict[str, bool]]:
        return {"voice_assistant": {"wake_word_enabled": bool(enabled)}}