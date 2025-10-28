from typing import Dict


class VoiceAssistantUsecase:
    """State helpers for controlling voice assistant behaviour."""

    def set_wake_word_enabled(self, enabled: bool) -> Dict[str, Dict[str, bool]]:
        enabled_bool = bool(enabled)
        print(f"[Usecase] set_wake_word_enabled -> {enabled_bool}")
        return {"voice_assistant": {"wake_word_enabled": enabled_bool}}