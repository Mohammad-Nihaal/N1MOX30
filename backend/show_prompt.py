from app.services.ai_service import generate_content
import inspect

source = inspect.getsource(generate_content)
start = source.find('prompt = f"""')
end = source.find('"""', start + 12)

print(source[start:end + 3])
