from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import smtplib
from email.mime.text import MIMEText

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load CSV data
df = pd.read_csv("data/users.csv")

class EmailRequest(BaseModel):
    to: str
    message: str

@app.get("/users")
async def get_users():
    return df.to_dict(orient="records")

@app.get("/users/filter")
async def filter_users(role: str = None, location: str = None):
    filtered_df = df
    if role:
        filtered_df = filtered_df[filtered_df['role'].str.contains(role, case=False)]
    if location:
        filtered_df = filtered_df[filtered_df['location'].str.contains(location, case=False)]
    return filtered_df.to_dict(orient="records")

@app.post("/send-email")
async def send_email(request: EmailRequest):
    # Configure your email settings
    smtp_server = "smtp.example.com"
    smtp_port = 587
    smtp_username = "your_username"
    smtp_password = "your_password"
    from_email = "your_email@example.com"

    # Create and send the email
    msg = MIMEText(request.message)
    msg['Subject'] = "New job opportunity"
    msg['From'] = from_email
    msg['To'] = request.to

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)