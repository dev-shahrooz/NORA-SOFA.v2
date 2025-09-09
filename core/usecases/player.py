from services.player_service import PlayerService

class PlayerUsecase:
    def __init__(self, service: PlayerService):
        self.service = service

    def _patch(self):
        status = self.service.status()
        meta = self.service.metadata()
        return {"player": {"status": status, **meta}}

    def play(self):
        self.service.play()
        return self._patch()

    def pause(self):
        self.service.pause()
        return self._patch()

    def next(self):
        self.service.next()
        return self._patch()

    def previous(self):
        self.service.previous()
        return self._patch()

    def info(self):
        return self._patch()