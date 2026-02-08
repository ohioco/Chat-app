from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

connections = []

@app.get("/")
async def get():
    return HTMLResponse("""
    <html>
        <head><title>Chat</title></head>
        <body>
            <h1>Chat Room</h1>
            <div id="messages"></div>
            <input id="msg" autocomplete="off"/>
            <button onclick="sendMessage()">Send</button>

            <script>
                const ws = new WebSocket(`ws://${location.host}/ws`);
                const messages = document.getElementById("messages");

                ws.onmessage = (event) => {
                    const p = document.createElement("p");
                    p.textContent = event.data;
                    messages.appendChild(p);
                };

                function sendMessage() {
                    const input = document.getElementById("msg");
                    ws.send(input.value);
                    input.value = "";
                }
            </script>
        </body>
    </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for conn in connections:
                await conn.send_text(data)
    except:
        connections.remove(websocket)
