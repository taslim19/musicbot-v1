from functools import wraps
import traceback

def capture_err(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred in {func.__name__}:")
            traceback.print_exc()
            return None
    return wrapper

capture_callback_err = capture_err 