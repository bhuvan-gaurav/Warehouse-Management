from sqlalchemy import Column, Integer, Float, String, create_engine, DateTime, func, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import pydantic

ph = PasswordHasher()

DB_PATH = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()
USERNAME = "Bhuvan"
PASSWORD = "Bhuvan123"   
ACCESS_TOKEN_EXPIRY_MINUTES = 1
REFRESH_TOKEN_EXPIRY = 7*24*60
SECRET_KEY = "SECRET001"
ALGORITHM = "HS256"

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    destination = Column(String)
    weight = Column(Float)
    arrival_date = Column(DateTime, default=datetime.today)
    status = Column(String)
    batch_id = Column(Integer, ForeignKey("dispatch_batches.id"), nullable=True)


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

Base.metadata.create_all(engine)

class DispatchBatch(Base):
    __tablename__ = "dispatch_batches"

    id = Column(Integer, primary_key=True)
    destination = Column(String)
    vehicle_number = Column(String)
    dispatch_date = Column(DateTime)
    status = Column(String)

Base.metadata.create_all(engine)


def add_package(name, destination, weight, arrival_date, status="pending"):
    session = Session(engine)
    package = Package(name=name, destination=destination, weight=weight, arrival_date=arrival_date, status=status)
    session.add(package)
    session.commit()
    response = {
        "id": package.id,
        "name": package.name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": package.arrival_date,
        "status": package.status
    }
    session.close()
    return response


def get_package(id):
    session = Session(engine)
    package = session.query(Package).filter(Package.id == id).first()
    response = None
    if package:
        response = {
            "id": package.id,
            "name": package.name,
            "destination": package.destination,
            "weight": package.weight,
            "arrival_date": package.arrival_date,
            "status": package.status,
            "dispatch_id": package.dispatch_id
        }
    session.close()
    return response


def delete_package(id):
    session = Session(engine)
    package = session.query(Package).filter(Package.id == id).first()
    session.delete(package)
    session.commit()
    session.close()
    return {"message": "Package deleted"}


def get_all_packages(destination=None, status=None, arrival_date=None):
    session = Session(engine)
    packages = session.query(Package)
    if destination:
        packages = packages.filter(Package.destination == destination)
    if status:
        packages = packages.filter(Package.status == status)
    if arrival_date:
        packages = packages.filter(Package.arrival_date == arrival_date)
    response = []
    for package in packages.all():
        temp_package = {
            "id": package.id,
            "name": package.name,
            "destination": package.destination,
            "weight": package.weight,
            "arrival_date": package.arrival_date,
            "status": package.status,
            "_id": package.batch_id
        }
        response.append(temp_package)
    session.close()
    return response

def get_summary():
    session = Session(engine)
    total = session.query(Package).count()
    pending = session.query(Package).filter(Package.status == "pending").count()
    dispatched = session.query(Package).filter(Package.status == "dispatched").count()
    summary = session.query(Package.destination, func.count(Package.id)).group_by(Package.destination).all()
    destinations = []
    for item in summary:
        temp_destination = {
            "destination": item[0],
            "count": item[1]
        }
        destinations.append(temp_destination)
    response = {
        "total_received": total,
        "total_pending": pending,
        "total_dispatched": dispatched,
        "destination_wise_count": destinations
    }
    session.close()
    return response


def add_dispatch(vehicle, destination, dispatch_date):
    session = Session(engine)
    dispatch = DispatchBatch(vehicle=vehicle, destination=destination, dispatch_date=dispatch_date, status="scheduled")
    session.add(dispatch)
    session.commit()
    packages = session.query(Package).filter(Package.destination == destination, Package.status == "pending").all()
    for package in packages:
        package.status = "dispatched"
        package.dispatch_id = dispatch.id
    session.commit()
    response = {
        "id": dispatch.id,
        "vehicle": dispatch.vehicle,
        "destination": dispatch.destination,
        "dispatch_date": dispatch.dispatch_date,
        "status": dispatch.status,
        "packages_dispatched": len(packages)
    }
    session.close()
    return response

def verify_login(username, password):
    session = Session(engine)
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        session.close()
        return False
    session.close()
    access_token = create_token(username, token_type="access")
    refresh_token = create_token(username, token_type="refresh")
    return {"access_token": access_token, "refresh_token": refresh_token}

def create_token(username, token_type):
    time = ACCESS_TOKEN_EXPIRY_MINUTES
    payload = {
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)

    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token, token_type):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return False
    if payload["token_type"] == token_type:
        return payload["username"]
    return False            

def register_user(username: str, password: str):
    session = Session(engine)
    user_exists = session.query(User).filter_by(username=username).first()
    if user_exists is not None:
        session.close()
        return False
    session.add(User(username=username, password=ph.hash(password)))
    session.commit()
    session.close()
    return True
