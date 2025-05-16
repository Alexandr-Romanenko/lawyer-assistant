import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ3Mjk1ODIwLCJpYXQiOjE3NDcyOTU1MjAsImp0aSI6IjNhOThjMjMwOTc4OTQ4ZDRiNmI4MDljOTJlMWNhOTk0IiwidXNlcl9pZCI6MX0.fYD64jRc4c7PjaHN1N9Od76k4IrkCMjZAzcdYKb2ZI8"
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)

import time
print(time.time())