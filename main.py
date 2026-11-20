import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import User
from security import hash_password,verify_password

load_dotenv()

SECRET_KEY = os.getenv("SESSION_SECRET")

if not SECRET_KEY:
    raise RuntimeError("SESSION_SECRET is missing in .env file")

app = FastAPI(title="Student Portal")

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=False
)

templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


# Home Page
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"request": request}
    )


# Registration Page
@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"request": request}
    )


# Registration Backend
@app.post("/register")
def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "request": request,
                "error": "All fields are required"
            },
            status_code=400
        )

    if len(password) < 8:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "request": request,
                "error": "Password must contain at least 8 characters"
            },
            status_code=400
        )

    # Check duplicate email
    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "request": request,
                "error": "Email already registered"
            },
            status_code=400
        )

    # Hash password
    hashed_password = hash_password(password)

    # Create new student
    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password,
        role="student"
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse(
        url="/login",
        status_code=303
    )
        # Login Page
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request}
    )


# Login Backend
@app.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    email = email.strip().lower()

    # Find user
    user = db.query(User).filter(
        User.email == email
    ).first()

    # Verify credentials
    if not user or not verify_password(
        password, user.password_hash
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "error": "Invalid email or password"
            },
            status_code=401
        )

    # Create session after successful login
    request.session.clear()
    request.session["user_id"] = user.id

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )
    # Login Page
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request}
    )


# Login Backend
@app.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    email = email.strip().lower()

    # Find user
    user = db.query(User).filter(
        User.email == email
    ).first()

    # Verify credentials
    if not user or not verify_password(
        password, user.password_hash
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "error": "Invalid email or password"
            },
            status_code=401
        )

    # Create session after successful login
    request.session.clear()
    request.session["user_id"] = user.id

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )
    # Login Page
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request}
    )


# Login Backend
@app.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    email = email.strip().lower()

    # Find user
    user = db.query(User).filter(
        User.email == email
    ).first()

    # Verify credentials
    if not user or not verify_password(
        password, user.password_hash
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "error": "Invalid email or password"
            },
            status_code=401
        )

    # Create session after successful login
    request.session.clear()
    request.session["user_id"] = user.id

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    
    )
    # Student Dashboard
@app.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    # Check whether user is logged in
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # Get student details
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        request.session.clear()
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "user": user
        }
    )
    # Admin Page
@app.get("/admin")
def admin_page(
    request: Request,
    db: Session = Depends(get_db)
):
    # Check login
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # Get user details
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        request.session.clear()
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # Check admin role
    if user.role != "admin":
        return templates.TemplateResponse(
            request=request,
            name="access_denied.html",
            context={"request": request},
            status_code=403
        )

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "request": request,
            "user": user
        }
    )
    # Logout
@app.get("/logout")
def logout(request: Request):
    # Clear user session
    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303
    )
    # Student List Backend
@app.get("/students")
def students_page(
    request: Request,
    db: Session = Depends(get_db)
):

    # Check login
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # Get logged-in user
    current_user = db.query(User).filter(
        User.id == user_id
    ).first()

    # Check admin permission
    if not current_user or current_user.role != "admin":
        return templates.TemplateResponse(
            request=request,
            name="access_denied.html",
            context={"request": request},
            status_code=403
        )

    # Get all registered students
    students = db.query(User).filter(
        User.role == "student"
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="students.html",
        context={
            "request": request,
            "students": students
        }
    )
    # Student Profile Backend
@app.get("/profile")
def student_profile(
    request: Request,
    db: Session = Depends(get_db)
):

    # Check login session
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # Get student details
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        request.session.clear()

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # Display profile page
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "request": request,
            "user": user
        }
    )
    # Logout Backend
@app.get("/logout")
def logout_user(request: Request):

    # Clear user login session
    request.session.clear()

    # Redirect to login page
    return RedirectResponse(
        url="/login",
        status_code=303
    )
    # Admin Dashboard Backend
@app.get("/admin")
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    # Check login session
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # Get logged-in user
    current_user = db.query(User).filter(
        User.id == user_id
    ).first()

    # Check admin role
    if not current_user or current_user.role != "admin":
        return templates.TemplateResponse(
            request=request,
            name="access_denied.html",
            context={"request": request},
            status_code=403
        )

    # Count registered students
    total_students = db.query(User).filter(
        User.role == "student"
    ).count()

    # Display admin dashboard
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "request": request,
            "user": current_user,
            "total_students": total_students
        }
    )
    # Custom 404 Error Handler
@app.exception_handler(404)
async def page_not_found(request: Request, exc):

    return templates.TemplateResponse(
        request=request,
        name="404.html",
        context={
            "request": request
        },
        status_code=404
    )
