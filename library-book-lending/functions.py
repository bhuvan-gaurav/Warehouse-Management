from fastapi import FastAPI, HTTPException,Header,Body
from fastapi.middleware.cors import CORSMiddleware
import functions    
from pydantic import BaseModel

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str
    total_copies: int
    genre: str

class LoanCreate(BaseModel):
    book_id: int
    roll_no: str

class BookUpdate(BaseModel):
    total_copies: int


GENRES = ["textbook", "fiction", "reference", "magazine", "biography"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


@app.get("/books/{book_id}")
def get_book(book_id: int):
    results=functions.get_book(book_id = book_id)
    if not results:
        raise HTTPException(status_code=404, detail="Book not found")
    return results


@app.post("/books")
def add_book(data: BookCreate):
    if data.title == "" or data.author == "" or data.genre == "":
        raise HTTPException(status_code=422, detail="Fields can't be empty")

    if data.total_copies < 1 or data.total_copies > 20:
        raise HTTPException(status_code=422, detail="total_copies must be between 1 and 20")

    if data.genre not in GENRES:
        raise HTTPException(status_code=422, detail="Invalid genre")

    result = functions.add_new_book(
        title=data.title,
        author=data.author,
        total_copies=data.total_copies,
        genre=data.genre
    )
    return result

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    result=functions.delete_book(book_id=book_id)
    if result is None:
        raise HTTPException(status_code=404,detail="Book not found")
    if result=="on_loan":
        raise HTTPException(status_code=400,detail="Book has copies out on loan")
    return result

@app.get("/books")
def menu(genre: str = None, title: str = None):
    if genre is not None and genre not in GENRES:
        raise HTTPException(status_code=422,detail="Invalid genre")
    result= functions.get_all_books(genre=genre, title=title)
    return result



@app.patch("/books/{book_id}")
def update_total_copies(book_id: int, data: BookUpdate):
    result = functions.update_total_copies(
        book_id=book_id,
        new_total_copies=data.total_copies
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if result == "below_loans":
        raise HTTPException(status_code=400, detail="Total copies below copies on loan")

    return result

@app.patch("/loans/{loan_id}/return")
def return_loan(loan_id: int):
    result=functions.loan_return(loan_id)
    if result is None:
        raise HTTPException(status_code=404,detail="Loan not found")
    if result=="already_returned":
        raise HTTPException(status_code=400,detail="Loan already returned")
    return result

@app.patch("/loans/{loan_id}/renew")
def loan_renew(loan_id: int):
    result=functions.loan_renewal(loan_id)
    if result is None:
        raise HTTPException(status_code=404,detail="Loan not found")
    if result=="already_returned":
        raise HTTPException(status_code=400,detail="Loan already returned")
    if result=="already_renewed":
        raise HTTPException(status_code=400,detail="Loan already renewed")
    if result=="overdue":
        raise HTTPException(status_code=400,detail="Loan is overdue")
    return result

@app.get("/loans/student/{roll_no}")
def loan_student(roll_no: str):
    result=functions.student_loans(roll_no)
    if result is None:
        raise HTTPException(status_code=404,detail="Student not found")
    return result

@app.get("/loans/overdue")
def overdue():
    result=functions.loans_overdue()
    return result


@app.post("/loans")
def borrow(data: LoanCreate):
    if data.roll_no == "":
        raise HTTPException(status_code=422, detail="Roll number can't be empty")

    result = functions.borrow_book(data.book_id, data.roll_no)

    if result is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if result == "no_copies":
        raise HTTPException(status_code=400, detail="No copies available")
    if result == "max_loans":
        raise HTTPException(status_code=400, detail="Maximum loans reached")
    if result == "has_overdue":
        raise HTTPException(status_code=400, detail="You have overdue books")
    if result == "already_has":
        raise HTTPException(status_code=400, detail="You already borrowed this book")

    return result

@app.post("/login")
def login(username= Body(), password= Body()):
    token = functions.verify_login(username=username, password=password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return token

@app.post("/refresh")
def refresh_token(refresh_token=Header(None)):
    username=functions.verify_token(token=refresh_token, token_type="refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    access_token = functions.create_token(username=username, token_type="access")
    return {"access_token": access_token}

@app.post("/register")
def register_user(user_name= Body(), password=Body()):
    if functions.register_user(user_name=user_name,password=password):
        return{"message":"user registered successfully"}
    raise HTTPException(status_code=400, detail="user already exists")