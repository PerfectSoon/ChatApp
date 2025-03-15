from typing import Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

class Manager:
    def __init__(self):
        self.connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, room_id: int, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.connections:
            self.connections[room_id] = set()
        self.connections[room_id].add(websocket)

    def disconnect(self, room_id: int, websocket: WebSocket):
        if room_id in self.connections:
            self.connections[room_id].discard(websocket)
            if not self.connections[room_id]:
                del self.connections[room_id]


    async def broadcast(self, room_id: int, message: str):
        if room_id not in self.connections:
            return

        to_remove = []
        for websocket in self.connections[room_id]:
            if websocket.application_state == "DISCONNECTED":
                to_remove.append(websocket)
            else:
                try:
                    await websocket.send_text(message)
                except RuntimeError:
                    to_remove.append(websocket)

        for websocket in to_remove:
            self.connections[room_id].remove(websocket)


manager = Manager()