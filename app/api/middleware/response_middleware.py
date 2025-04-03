from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from fastapi import Request
import json
import traceback

class ResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)

            # Handle StreamingResponse properly
            if isinstance(response, Response) and response.status_code == 200:
                # Read response body safely
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk

                # Ensure the content type is JSON
                try:
                    body_content = json.loads(body.decode())
                except json.JSONDecodeError:
                    body_content = None  # Handle cases where the response is empty or not JSON

                return JSONResponse(
                    content={
                        "success": True,
                        "message": "Request successful",
                        "data": body_content,
                    },
                    status_code=200
                )

            return response  # Return other responses as they are

        except Exception as e:
            traceback.print_exc()
            return JSONResponse(
                content={
                    "success": False,
                    "message": str(e),
                    "error_code": 500
                },
                status_code=500
            )
