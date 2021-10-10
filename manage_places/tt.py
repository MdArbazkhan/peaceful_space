from dotenv import load_dotenv
load_dotenv()
import os
print(os.environ.get('ALLOWED_HOSTS'))
print(os.environ.get("DEBUG"))