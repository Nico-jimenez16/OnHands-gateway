import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.chat_service import ChatService
from core.settings import settings

router = APIRouter()

chat_service = ChatService(base_url=settings.CORE_SERVICE_URL)


class StartConversationBody(BaseModel):
    initial_message: str


class SendMessageBody(BaseModel):
    message: str


class ChatBody(BaseModel):
    message: str
    requestId: str | None = None
    conversationHistory: list[dict] = []
    user_id: str = "anonymous"


_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _sse_frame(frame: dict) -> str:
    return f"data: {json.dumps(frame, ensure_ascii=False)}\n\n"


async def _build_chat_frame(body: ChatBody) -> dict:
    try:
        if body.requestId:
            payload = await chat_service.send_message(body.requestId, body.user_id, body.message)
        else:
            payload = await chat_service.start_conversation(body.user_id, body.message)
        return {
            "type": "message",
            "payload": {
                "reply": payload.get("reply", ""),
                "isComplete": bool(payload.get("is_complete", False)),
                "requestId": payload.get("request_id") or payload.get("conversation_id"),
                "extractedData": payload.get("extracted") or None,
            },
        }
    except HTTPException as e:
        detail = e.detail if isinstance(e.detail, str) else json.dumps(e.detail, ensure_ascii=False)
        return {"type": "error", "payload": {"message": detail}}
    except Exception as e:
        return {"type": "error", "payload": {"message": str(e)}}


@router.post("", summary="Chat unificado (SSE) para el frontend")
async def chat_endpoint(body: ChatBody):
    frame = await _build_chat_frame(body)

    async def streamer():
        yield _sse_frame(frame)

    return StreamingResponse(streamer(), media_type="text/event-stream", headers=_SSE_HEADERS)


@router.post("/conversations", summary="Iniciar una conversación con el asistente")
async def start_conversation(request: Request, body: StartConversationBody):
    try:
        user_id = request.headers.get("x-user-id", "anonymous")
        return await chat_service.start_conversation(user_id, body.initial_message)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al conectar con el CoreService: {e}")


@router.post("/conversations/{conversation_id}/messages", summary="Enviar un mensaje a una conversación existente")
async def send_message(conversation_id: str, request: Request, body: SendMessageBody):
    try:
        user_id = request.headers.get("x-user-id", "anonymous")
        return await chat_service.send_message(conversation_id, user_id, body.message)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al conectar con el CoreService: {e}")
