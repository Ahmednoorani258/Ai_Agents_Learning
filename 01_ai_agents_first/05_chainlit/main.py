import chainlit as cl

@cl.on_chat_start
async def start():
    await cl.Message(content="Hello! How can I help you today?").send()
    
@cl.on_message
async def handle_message(message:cl.Message):
    # Here you can implement your logic to process the message
    response = f"You said: {message.content}"
    
    # Send the response back to the user
    await cl.Message(content=response).send()

# @cl.on_error
# async def handle_error(error: Exception):
#     # Handle any errors that occur during the chat
#     await cl.Message(content=f"An error occurred: {str(error)}").send()
    
@cl.on_chat_end
async def end_chat():
    await cl.Message(content="Thank you for chatting!").send()
# This is a simple Chainlit application that responds to user messages.