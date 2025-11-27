from google import genai
from google.genai import types
import inspect

print("HttpOptions fields:")
try:
    # It might be a Pydantic model or a TypedDict
    if hasattr(types.HttpOptions, "__annotations__"):
        print(types.HttpOptions.__annotations__)
    else:
        print(dir(types.HttpOptions))
except Exception as e:
    print(e)

