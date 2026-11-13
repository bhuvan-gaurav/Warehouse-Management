from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import functions
from pydantic import BaseModel
from fastapi import Header, Body

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PackageCreate(BaseModel):
    name: str
    destination: str
    weight: float
    status: str = "pending"

class PackageUpdate(BaseModel):
    name: str = None
    destination: str = None
    weight: float = None
    status: str = None

class BatchCreate(BaseModel):
    destination: str
    vehicle: str
    package_ids: str
    dispatch_status: str = "scheduled"

class UserAuthorize(BaseModel):
    username: str
    password: str
    role: str = "staff"

@app.post("/packages")
def register_package(pkg: PackageCreate, token=Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return functions.add_package(name=pkg.name, destination=pkg.destination, weight=pkg.weight, status=pkg.status)

@app.get("/packages/{id}")
def get_package(id: int, token=Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    pkg = functions.get_package(id)
    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")
    return pkg

@app.patch("/packages/{id}")
def update_package(id: int, pkg: PackageUpdate, token=Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    updated = functions.update_package(id=id, name=pkg.name, destination=pkg.destination, weight=pkg.weight, status=pkg.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Package not found")
    return updated

@app.delete("/packages/{id}")
def delete_package(id: int, token=Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    result = functions.delete_package(id)
    if result == "not_found":
        raise HTTPException(status_code=404, detail="Package not found")
    if result == "dispatched":
        raise HTTPException(status_code=400, detail="Cannot delete a dispatched package")
    return {"message": "Package deleted"}

@app.post("/login")
def login(user: UserAuthorize):
    token = functions.verify_login(username=user.username, password=user.password)
    if not token:
        raise HTTPException(status_code=401, detail="invalid username or password")
    return token

@app.post("/refresh")
def refresh(refresh_token=Header(None)):
    user = functions.verify_token(token=refresh_token, token_type="refresh")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    access_token = functions.create_token(username=user["username"], role=user["role"], token_type="access")
    return {"access_token": access_token}

@app.get("/packages")
def search_packages(destination=None, status=None, arrival_date=None, token=Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return functions.get_packages(destination=destination, status=status, arrival_date=arrival_date)

@app.get("/analytics")
def warehouse_analytics(token=Header(None)):
    user = functions.verify_token(token=token, token_type="access")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view analytics")
    return functions.get_warehouse_analytics()

@app.get("/batches")
def view_batches(destination=None, vehicle=None, dispatch_status=None, token=Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return functions.get_dispatch_batches(destination=destination, vehicle=vehicle, dispatch_status=dispatch_status)

@app.post("/batches")
def add_batch(batch: BatchCreate, token=Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return functions.create_dispatch_batch(
        destination=batch.destination,
        vehicle=batch.vehicle,
        package_ids=batch.package_ids,
        dispatch_status=batch.dispatch_status
    )

@app.post("/register")
def register_user(user: UserAuthorize):
    if functions.register_user(user_name=user.username, password=user.password, role=user.role):
        return {"message": "user registered successfully"}
    raise HTTPException(status_code=400, detail="User already exists")