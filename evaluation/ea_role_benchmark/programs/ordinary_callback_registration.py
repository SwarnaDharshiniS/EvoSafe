"""A non-EA event callback registration and dispatch."""
callbacks = create_callback_registry()

def log_message(message):
    return message.strip()

callbacks.register("on_message", log_message)
result = callbacks.invoke_registered("on_message", " hello ")
