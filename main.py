from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from Database import DatabaseHandler
import uvicorn

db = DatabaseHandler()

app = FastAPI(
    title="FastConcierge",
    description="Concierge Service API",
    version="0.1"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str

class Booking(BaseModel):
    room_id: str
    hotel_id: str
    booking_date: str
    guest_name: str
    guest_phone: str
    payment_method: str

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        response = db.client.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })

        return {
            "access_token": response.session.access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Incorrect email or password")
    
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user = db.client.auth.get_user(token)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@app.get("/user-profile/")
async def get_user_profile(current_user= Depends(get_current_user)):
    try:
        response = db.client.table("profiles").select("*").eq("id", current_user.user.id).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail="User profile not found")
    
@app.get("/")
async def root():
    return {"message": "Hello Worlds"}

@app.get("/bookings/")
async def get_bookings():
    try:
        response = db.client.table("bookings").select("*").execute()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/booking/{booking_id}")
async def get_booking_by_id(booking_id: str):
    try:
        response = db.client.table("bookings").select("*").eq("booking_id", booking_id).execute()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/booking/")
async def create_booking(booking: Booking):
    try:
        booking_data = booking.model_dump()
        print(booking_data)
        response = db.client.table("bookings").insert(booking_data).execute()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
@app.put("/booking/{booking_id}")
async def update_booking(booking_id: str, booking: Booking):
    try:
        booking_data = booking.model_dump()
        response = db.client.table("bookings").update(booking_data).eq("booking_id", booking_id).execute()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/booking/{booking_id}")
async def delete_booking(booking_id: str):
    try:
        response = db.client.table("bookings").delete().eq("booking_id", booking_id).execute()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/hotel-rooms/")
async def search_hotel_rooms(room_type: str = None, is_ascending: bool = False):
    try:
        query = db.client.table("hotel_rooms").select("*")

        if room_type:
            query = query.eq("room_type", room_type)

        if is_ascending:
            query = query.order("price_USD", desc=False)
        else:
            query = query.order("price_USD", desc=True)

        response = query.execute()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)