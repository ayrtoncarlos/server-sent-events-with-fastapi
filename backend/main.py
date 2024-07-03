import ast
import json
from asyncio import sleep
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


progress_value = 0


def update_progress():
    global progress_value
    if progress_value < 100:
        progress_value += 10


async def get_progress_value():
    """
    Note - Here \\n is intetionally added as to document the actual data instead of using i as new line.

    1. SSE messages are sent as a stream of text events, where each event is a separate piece of data. Each event consists of one or more lines. The minimum requirement for a line is to start with data: followed by the payload. Here's a simple example:
        data: This is a message\\n\\n

    2. SSE allows for optional fields in an event. Common fields include id, event, and retry. For example:
        id: 123
        event: customEvent
        data: Custom event message\\n\\n

    3.If the connection is closed, the client can attempt to reconnect. The server can include a retry field to suggest the time in milliseconds that the client should wait before attempting to reconnect.
        retry: 5000

    example.
    Below This format is necessary. Either event keyword or data keyword corresponding to that will be actual content

    ---------------------------------------

    yield f'event: ss\\ndata: food\\n\\n'

    data = {"eventNo": i, "message": "This is a message"}
    yield f"event: message\\ndata: {json.dumps(data)}\\n\\n"

    data = {"eventNo": i, "message": "This is a update"}
    yield f"event: update\\ndata: {json.dumps(data)}\\n\\n"


    progress_json = open("progress.json")
    progress_values = json.load(progress_json)
    for progress in progress_values[0:10]:
        data = json.dumps(progress)
        data = ast.literal_eval(data)
        yield str(data["progress"])
        await sleep(1)
    """
    global progress_value
    data = {"progress": progress_value}
    data = json.dumps(data)
    return f"event: progressUpdate\ndata: {data}\n\n"
    #await sleep(1)


@app.get("/get-progress")
async def get_progress():
    """
    Set the Content-Type header to "text/event-stream" to indicate that the response should be interpreted as Server-Sent Events.
    """
    value = await get_progress_value()
    print(f"VALUE: {value}")

    update_progress()
    return StreamingResponse(str(value), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
