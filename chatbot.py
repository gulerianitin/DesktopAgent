"""
Desktop Agent - Unified Interface
Chatbot + VNC Desktop in one browser window
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import List, Dict, AsyncGenerator
import time
import json
import asyncio
from langchain.callbacks.base import BaseCallbackHandler

from agents.desktop_agent import create_desktop_agent

load_dotenv()

app = FastAPI(title="Desktop Agent Unified", version="3.0.0")


class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler to capture agent activity for streaming."""

    def __init__(self):
        self.events = []

    def on_tool_start(self, serialized, input_str: str, **kwargs):
        """Called when a tool starts executing."""
        tool_name = serialized.get("name", "unknown")
        self.events.append({
            "type": "tool_start",
            "tool": tool_name,
            "input": str(input_str)[:200]
        })

    def on_tool_end(self, output: str, **kwargs):
        """Called when a tool finishes executing."""
        self.events.append({
            "type": "tool_end",
            "output": str(output)[:500]
        })

    def on_tool_error(self, error, **kwargs):
        """Called when a tool errors."""
        self.events.append({
            "type": "tool_error",
            "error": str(error)[:300]
        })

    def on_agent_action(self, action, **kwargs):
        """Called when agent takes an action."""
        self.events.append({
            "type": "agent_action",
            "tool": action.tool,
            "input": str(action.tool_input)[:200]
        })

    def on_llm_start(self, serialized, prompts, **kwargs):
        """Called when LLM starts."""
        self.events.append({
            "type": "thinking",
            "message": "Agent is thinking..."
        })

class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.agent = create_desktop_agent(verbose=True)  # Enable verbose for better logging
        self.execution_logs = []
        self.streaming_callback = None

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        self.execution_logs.append(f"[{timestamp}] {message}")

sessions: Dict[str, Session] = {}

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    intermediate_steps: List[str] = []
    execution_logs: List[str] = []

# Unified HTML with split-screen: Chatbot + VNC
UNIFIED_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Desktop Agent - Unified Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: #1a1a2e;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }

        .header h1 {
            font-size: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .header .badge {
            background: rgba(255,255,255,0.2);
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 11px;
        }

        .main-container {
            flex: 1;
            display: flex;
            gap: 10px;
            padding: 10px;
            overflow: hidden;
        }

        /* Chatbot Panel - Left Side */
        .chatbot-panel {
            flex: 0 0 400px;
            display: flex;
            flex-direction: column;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .chatbot-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: 600;
        }

        .examples {
            display: flex;
            gap: 8px;
            padding: 10px;
            overflow-x: auto;
            background: #f7f8fc;
            border-bottom: 1px solid #e1e4e8;
        }

        .example-chip {
            padding: 6px 12px;
            background: white;
            border: 1px solid #e1e4e8;
            border-radius: 15px;
            font-size: 12px;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
        }

        .example-chip:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #f7f8fc;
        }

        .message {
            margin-bottom: 15px;
            display: flex;
            gap: 10px;
            animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            justify-content: flex-end;
        }

        .message-content {
            max-width: 85%;
            padding: 10px 14px;
            border-radius: 15px;
            line-height: 1.4;
            font-size: 14px;
            white-space: pre-wrap;
        }

        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .message.assistant .message-content {
            background: white;
            color: #333;
            border: 1px solid #e1e4e8;
        }

        .input-container {
            padding: 15px;
            background: white;
            border-top: 1px solid #e1e4e8;
        }

        .input-wrapper {
            display: flex;
            gap: 8px;
        }

        #messageInput {
            flex: 1;
            padding: 10px 14px;
            border: 2px solid #e1e4e8;
            border-radius: 20px;
            font-size: 14px;
            outline: none;
        }

        #messageInput:focus {
            border-color: #667eea;
        }

        #sendButton {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
        }

        #sendButton:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        /* VNC Panel - Right Side */
        .vnc-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #0f3460;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .vnc-header {
            background: #16213e;
            color: white;
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .vnc-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4ade80;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .vnc-container {
            flex: 1;
            position: relative;
            background: #000;
        }

        #vncIframe {
            width: 100%;
            height: 100%;
            border: none;
        }

        .vnc-loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            text-align: center;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255,255,255,0.1);
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>
            <span>🤖</span>
            <span>Desktop Agent - Unified Interface</span>
        </h1>
        <div class="badge">Chatbot + VNC Desktop</div>
    </div>

    <div class="main-container">
        <!-- Chatbot Panel -->
        <div class="chatbot-panel">
            <div class="chatbot-header">
                AI Assistant
            </div>

            <div class="examples">
                <div class="example-chip" onclick="sendExample('Install GIMP')">GIMP</div>
                <div class="example-chip" onclick="sendExample('Install Firefox')">Firefox</div>
                <div class="example-chip" onclick="sendExample('Install VLC')">VLC</div>
                <div class="example-chip" onclick="sendExample('System info')">System</div>
            </div>

            <div class="chat-container" id="chatContainer">
                <div class="message assistant">
                    <div class="message-content">
                        <strong>Welcome to Desktop Agent! 🚀</strong><br><br>
                        <strong>Left panel (this):</strong> Chat with AI to install apps<br>
                        <strong>Right panel:</strong> VNC desktop - watch apps launch!<br><br>
                        Try: "Install GIMP" then launch it in VNC! →
                    </div>
                </div>
            </div>

            <div class="input-container">
                <div class="input-wrapper">
                    <input
                        type="text"
                        id="messageInput"
                        placeholder="Ask me to install software..."
                        onkeypress="handleKeyPress(event)"
                    />
                    <button id="sendButton" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>

        <!-- VNC Panel -->
        <div class="vnc-panel">
            <div class="vnc-header">
                <div>
                    <strong>🖥️ Desktop Environment</strong>
                </div>
                <div class="vnc-status">
                    <span class="status-dot"></span>
                    <span>Connected</span>
                </div>
            </div>
            <div class="vnc-container">
                <div class="vnc-loading" id="vncLoading">
                    <div class="spinner"></div>
                    <div>Loading VNC Desktop...</div>
                </div>
                <iframe id="vncIframe" src="http://localhost:6080/vnc.html?autoconnect=true&resize=scale"></iframe>
            </div>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');

        // Hide loading when iframe loads
        document.getElementById('vncIframe').addEventListener('load', function() {
            setTimeout(() => {
                document.getElementById('vncLoading').style.display = 'none';
            }, 2000);
        });

        function addMessage(content, isUser = false, isActivity = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
            if (isActivity) {
                messageDiv.className += ' activity';
            }

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';

            let formattedContent = content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/`(.*?)`/g, '<code>$1</code>')
                .replace(/\n/g, '<br>');

            contentDiv.innerHTML = formattedContent;
            messageDiv.appendChild(contentDiv);

            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            return messageDiv;
        }

        function addActivityMessage(content) {
            const activityDiv = document.createElement('div');
            activityDiv.className = 'message activity';
            activityDiv.style.fontSize = '12px';
            activityDiv.style.opacity = '0.8';

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.innerHTML = content;

            activityDiv.appendChild(contentDiv);
            chatContainer.appendChild(activityDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            return activityDiv;
        }

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            messageInput.disabled = true;
            sendButton.disabled = true;
            sendButton.textContent = 'Working...';

            addMessage(message, true);
            messageInput.value = '';

            let currentActivity = null;

            try {
                // Use EventSource for Server-Sent Events
                const encodedMessage = encodeURIComponent(message);
                const eventSource = new EventSource(`/api/chat/stream?message=${encodedMessage}&session_id=unified`);

                eventSource.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);

                        if (data.type === 'start') {
                            currentActivity = addActivityMessage('🚀 ' + data.message);
                        }
                        else if (data.type === 'thinking') {
                            if (currentActivity) currentActivity.remove();
                            currentActivity = addActivityMessage('🤔 ' + data.message);
                        }
                        else if (data.type === 'agent_action') {
                            if (currentActivity) currentActivity.remove();
                            currentActivity = addActivityMessage(`🔧 Using tool: <strong>${data.tool}</strong>`);
                        }
                        else if (data.type === 'tool_start') {
                            if (currentActivity) currentActivity.remove();
                            const toolInput = data.input.length > 100 ? data.input.substring(0, 100) + '...' : data.input;
                            currentActivity = addActivityMessage(`⚙️ <strong>${data.tool}</strong> → ${toolInput}`);
                        }
                        else if (data.type === 'tool_end') {
                            if (currentActivity) {
                                // Show output preview
                                const output = data.output.length > 200 ? data.output.substring(0, 200) + '...' : data.output;
                                currentActivity.querySelector('.message-content').innerHTML += `<br><span style="opacity: 0.7">Result: ${output.replace(/\n/g, '<br>')}</span>`;
                            }
                        }
                        else if (data.type === 'tool_error') {
                            if (currentActivity) currentActivity.remove();
                            currentActivity = addActivityMessage(`❌ Error: ${data.error}`);
                        }
                        else if (data.type === 'final') {
                            if (currentActivity) currentActivity.remove();
                            addMessage(data.message, false);
                        }
                        else if (data.type === 'error') {
                            if (currentActivity) currentActivity.remove();
                            addMessage('❌ Error: ' + data.message, false);
                        }
                        else if (data.type === 'done') {
                            if (currentActivity) currentActivity.remove();
                            eventSource.close();
                            messageInput.disabled = false;
                            sendButton.disabled = false;
                            sendButton.textContent = 'Send';
                            messageInput.focus();
                        }
                    } catch (e) {
                        console.error('Error parsing event:', e);
                    }
                };

                eventSource.onerror = (error) => {
                    console.error('EventSource error:', error);
                    if (currentActivity) currentActivity.remove();
                    addMessage('❌ Connection error. Please try again.', false);
                    eventSource.close();
                    messageInput.disabled = false;
                    sendButton.disabled = false;
                    sendButton.textContent = 'Send';
                    messageInput.focus();
                };

            } catch (error) {
                addMessage('❌ Error: ' + error.message, false);
                messageInput.disabled = false;
                sendButton.disabled = false;
                sendButton.textContent = 'Send';
                messageInput.focus();
            }
        }

        function sendExample(text) {
            messageInput.value = text;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        messageInput.focus();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_unified_interface():
    """Serve unified chatbot + VNC interface"""
    return UNIFIED_HTML

@app.get("/api/chat/stream")
async def chat_stream(message: str, session_id: str = "unified"):
    """Stream chat response with real-time updates."""

    async def event_generator():
        try:
            # Initialize session
            if session_id not in sessions:
                sessions[session_id] = Session(session_id)

            session = sessions[session_id]
            session.execution_logs = []

            # Send initial message
            yield f"data: {json.dumps({'type': 'start', 'message': 'Starting...'})}\n\n"
            await asyncio.sleep(0.1)

            # Create callback handler
            callback = StreamingCallbackHandler()

            # Run agent in thread to avoid blocking
            import threading
            result = {"output": None, "error": None}

            def run_agent():
                try:
                    agent_result = session.agent.agent_executor.invoke(
                        {"input": message},
                        config={"callbacks": [callback]}
                    )
                    result["output"] = agent_result
                except Exception as e:
                    result["error"] = str(e)

            thread = threading.Thread(target=run_agent)
            thread.start()

            # Stream events as they happen
            sent_event_count = 0
            while thread.is_alive() or sent_event_count < len(callback.events):
                # Send new events
                while sent_event_count < len(callback.events):
                    event = callback.events[sent_event_count]
                    yield f"data: {json.dumps(event)}\n\n"
                    sent_event_count += 1
                    await asyncio.sleep(0.1)

                await asyncio.sleep(0.2)

            # Wait for thread to complete
            thread.join(timeout=300)

            # Send final result
            if result["error"]:
                yield f"data: {json.dumps({'type': 'error', 'message': result['error']})}\n\n"
            elif result["output"]:
                output = result["output"]["output"]
                if isinstance(output, list):
                    response_text = ""
                    for block in output:
                        if isinstance(block, dict) and block.get("type") == "text":
                            response_text += block.get("text", "")
                        elif hasattr(block, "text"):
                            response_text += block.text
                    output = response_text or str(output)
                elif not isinstance(output, str):
                    output = str(output)

                yield f"data: {json.dumps({'type': 'final', 'message': output})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Process chat message (non-streaming fallback)"""
    try:
        if message.session_id not in sessions:
            sessions[message.session_id] = Session(message.session_id)

        session = sessions[message.session_id]
        session.execution_logs = []
        session.log(f"User request: {message.message}")

        result = session.agent.run(message.message)

        # Handle response format
        output = result["output"]
        if isinstance(output, list):
            response_text = ""
            for block in output:
                if isinstance(block, dict) and block.get("type") == "text":
                    response_text += block.get("text", "")
                elif hasattr(block, "text"):
                    response_text += block.text
            output = response_text or str(output)
        elif not isinstance(output, str):
            output = str(output)

        tool_names = []
        for step in result.get("intermediate_steps", []):
            if len(step) >= 1:
                action = step[0]
                if hasattr(action, 'tool'):
                    tool_names.append(action.tool)

        session.log(f"Agent completed with {len(tool_names)} tool calls")

        return ChatResponse(
            response=output,
            intermediate_steps=tool_names,
            execution_logs=session.execution_logs
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "interface": "unified",
        "sessions": len(sessions)
    }

if __name__ == "__main__":
    import uvicorn
    print("🤖 Starting Desktop Agent - Unified Interface")
    print("🌐 Chatbot + VNC Desktop in one window!")
    print("📡 Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
