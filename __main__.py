
import gradio as gr
from typing import List, AsyncIterator
from agent import (
    root_agent as routing_agent,
)  
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from google.genai import types
from pprint import pformat
import asyncio
import traceback
import time  


APP_NAME = "Disaster Management Agent"
USER_ID = "user123"
SESSION_ID = "session123"

SESSION_SERVICE = InMemorySessionService()
ROUTING_AGENT_RUNNER = Runner(
    agent=routing_agent,
    app_name=APP_NAME,
    session_service=SESSION_SERVICE,
)


async def get_response_from_agent(
    message: str,
    history: List[gr.ChatMessage],
) -> AsyncIterator[gr.ChatMessage]:
    """Get response from host agent."""
    try:
        events_iterator: AsyncIterator[Event] = ROUTING_AGENT_RUNNER.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=types.Content(role="user", parts=[types.Part(text=message)]),
        )

        async for event in events_iterator:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:
                        formatted_call = f"```python\n{pformat(part.function_call.model_dump(exclude_none=True), indent=2, width=80)}\n```"
                        yield gr.ChatMessage(
                            role="assistant",
                            content=f"🛠️ **Tool Call: {part.function_call.name}**\n{formatted_call}",
                        )
                    elif part.function_response:
                        response_content = part.function_response.response
                        if (
                            isinstance(response_content, dict)
                            and "response" in response_content
                        ):
                            formatted_response_data = response_content["response"]
                        else:
                            formatted_response_data = response_content
                        formatted_response = f"```json\n{pformat(formatted_response_data, indent=2, width=80)}\n```"
                        yield gr.ChatMessage(
                            role="assistant",
                            content=f"⚡ **Tool Response from {part.function_response.name}**\n{formatted_response}",
                        )
            if event.is_final_response():
                final_response_text = ""
                if event.content and event.content.parts:
                    final_response_text = "".join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif event.actions and event.actions.escalate:
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                if final_response_text:
                    yield gr.ChatMessage(role="assistant", content=final_response_text)
                break
    except Exception as e:
        print(f"Error in get_response_from_agent (Type: {type(e)}): {e}")
        traceback.print_exc()  # This will print the full traceback
        yield gr.ChatMessage(
            role="assistant",
            content="An error occurred while processing your request. Please check the server logs for details.",
        )


async def main():
    """Main gradio app."""
    def slow_echo(message, history):
        for i in range(len(message)):
            time.sleep(0.05)
            yield "You typed: " + message[: i + 1]
    print("Creating ADK session...")
    await SESSION_SERVICE.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print("ADK session created successfully.")

    with gr.Blocks(theme=gr.themes.Ocean(), title="Disaster Management") as demo:

        gr.ChatInterface(
            get_response_from_agent,
            title="Disaster Management Assistant",
            description="This is a disaster management assistant that can help you with various tasks related to disaster response and management. You can ask questions, request information, or get assistance with specific tasks.",
            type="messages",
            flagging_mode="manual",
            flagging_options=["Like", "Spam", "Inappropriate", "Other"],
            save_history=True,
        )

    print("Launching Gradio interface...")
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=8080,
    )
    print("Gradio application has been shut down.")

if __name__ == "__main__":
    asyncio.run(main())
