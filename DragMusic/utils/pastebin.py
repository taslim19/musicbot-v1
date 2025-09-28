import aiohttp

async def paste(text: str) -> str:
    """Pastes the given text to a pastebin service and returns the link."""
    async with aiohttp.ClientSession() as session:
        # Using a simple, no-login-required pastebin service like hastebin
        try:
            response = await session.post("https://hastebin.com/documents", data=text.encode('utf-8'))
            response.raise_for_status()  # Will raise an exception for 4xx/5xx status
            result = await response.json()
            return f"https://hastebin.com/{result['key']}"
        except aiohttp.ClientError:
            return "Failed to connect to pastebin service."
        except Exception:
            # Fallback for other errors, e.g., if the service changes its response
            return "Failed to paste the content due to an unknown error."

# Alias for other parts of the code that expect DragBin
DragBin = paste
