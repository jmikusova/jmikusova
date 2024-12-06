import os
from datetime import datetime, timedelta

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, get_flashed_messages, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, allowed_file


# Configure application
app = Flask(__name__)

# Meal Type dicttionary
MEALTYPE = {
    "breakfast": "Breakfast",
    "lunch": "Lunch",
    "dinner": "Dinner",
    "snack": "Snack"
}
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
Session(app)

# SQLite database
db = SQL("sqlite:///tracker.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # clear session but still show flashes if present
    if session.get("_flashes"):
        flashes = session.get("_flashes")
        session.clear()
        session["_flashes"] = flashes
    else:
        session.clear()

     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username") or not request.form.get("password"):
            error = "Please complete the form."
            return render_template("login.html", error=error)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            error = "Invalid username or password."
            return render_template("login.html", error=error)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to homepage
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Ensure username and password were submitted
        if not username or not password:
            error = "Please complete the form."
            return render_template("register.html", error=error)

        # Ensure password confirmation was submitted and password match
        elif not request.form.get("confirmation") or not password == request.form.get("confirmation"):
            error = "Passwords do not match."
            return render_template("register.html", error=error)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            username
        )

        # Ensure username doesnt exist
        if len(rows) == 1:
            error = "Username already exists."
            return render_template("register.html", error=error)

        # INSERT the new user into users, hash of the user’s password
        hashed_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            hashed_password
            )

        flash("You are now registered! Please login.", "success")
        return redirect(url_for("login"))

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """homepage"""
    # User reached route via GET (as by clicking a link or via redirect)
    # week
    week_offset = int(request.args.get("week_offset", 0))
    current_date = datetime.now() + timedelta(weeks=week_offset)
    start_of_week = (current_date - timedelta(days=current_date.weekday() + 1)).date()
    end_of_week = start_of_week + timedelta(days=6)

    rows = db.execute(
        "SELECT id, date,meal_type,short_descr, photo_path FROM diary WHERE date BETWEEN ? AND ? AND user_id= ? ORDER BY date",
        start_of_week,
        end_of_week,
        session["user_id"]
        )

    # meals dictionary with dates as keys
    meals = {}
    for row in rows:
        date = row["date"]
        meal_type = row["meal_type"]
        day_name = datetime.strptime(str(date), "%Y-%m-%d").strftime("%A")

        if date not in meals:
            meals[date] = {"day_name": day_name,"breakfast": {}, "lunch": {}, "dinner": {},"snack":{}}

        # Store both the description and photo_path for each meal type
        meals[date][meal_type] = {
        "id": row["id"],
        "short_descr": row["short_descr"],
        "photo_path": row["photo_path"]}

    return render_template('index.html', meals=meals, start_of_week=start_of_week, week_offset=week_offset)

@app.route("/meal", methods=["GET", "POST"])
@login_required
def meal():
    """meal log"""

        # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        current_date = datetime.now().date()
        meal_id = request.args.get("meal_id")
        selected_meal_type = request.args.get("meal_type")
        prev_date = request.args.get("prev_date")
        date = prev_date if prev_date else current_date
        existing_meal = None


        #If existing meal from index.html
        if meal_id:
            # Get existing meal for editing
            existing_meal = db.execute("SELECT * FROM diary WHERE id = ? AND user_id = ?",
                                       meal_id,
                                       session["user_id"]
                                       )
            if not existing_meal:
                flash("Meal not found.", "danger")
                return redirect(url_for("index"))
            return render_template("meal.html", meal_type=MEALTYPE, existing_meal=existing_meal, date=existing_meal[0]["date"])
        else:
            #new meal redirected from navbar(current_date) or index.html(prev_date)
            return render_template("meal.html", meal_type=MEALTYPE, existing_meal=existing_meal, date=date, selected_meal_type=selected_meal_type )

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        current_date = datetime.now().date()
        meal_id = request.form.get("meal_id")
        meal_short = request.form.get("meal_short")
        meal_long = request.form.get("meal_long")
        meal_type = request.form.get("meal_type")
        photo = request.files['photo']
        selected_date = request.form.get("date") # Can be prev_date or current_date

        print("meal_short:", meal_short)
        print("meal_type:", meal_type)

        # Validate inputs
        if not meal_short or not meal_type:
            error = "Short description and meal type are required."
            return render_template("meal.html", date=selected_date, meal_type=MEALTYPE, error=error)


        #validated photo if provided
        photo_path = None
        if photo and allowed_file(photo.filename):
            filename = f"{meal_type}_{selected_date}_{photo.filename}"
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)

        if not meal_id:  # Add a new meal
            # Check for duplicate meal entries
            existing_entry = db.execute(
                "SELECT id FROM diary WHERE user_id = ? AND meal_type = ? AND date = ?",
                session["user_id"],
                meal_type,
                selected_date
            )
            if existing_entry:
                warning = f"A meal of type '{meal_type}' already exists for {selected_date}. Do you want to replace it?"
                return render_template(
                    "meal.html",
                    date=selected_date,
                    meal_type=MEALTYPE,
                    warning=warning,
                    new_meal={"meal_short": meal_short, "meal_long": meal_long, "photo_path": photo_path}
                )


            #Record the data into the diary table
            db.execute(
                "INSERT INTO diary (user_id, date, meal_type, short_descr, long_descr, photo_path) VALUES (?, ?, ?, ?, ?, ?)",
                session["user_id"],
                selected_date,
                meal_type,
                meal_short,
                meal_long,
                photo_path
            )
            flash("Meal added successfully.", "success")
            return redirect(url_for("index"))


        else: # If meal_ID exist, update existng mea record
            existing_meal = db.execute("SELECT * FROM diary WHERE id = ? AND user_id = ?",
                                       meal_id,
                                       session["user_id"]
                                       )
            if not existing_meal:
                flash("Meal not found.", "danger")
                return redirect(url_for("index"))

            # Extract the first (and only) meal record
            existing_meal = existing_meal[0]

            #Validate photo and replace the old one if present
            if not photo:
                photo_path = existing_meal["photo_path"]
            elif existing_meal["photo_path"] and os.path.exists(existing_meal["photo_path"]):
                os.remove(existing_meal["photo_path"])  # Remove old photo

            # Update existing meal
            db.execute( "UPDATE diary SET short_descr = ?, long_descr = ?, photo_path = ? WHERE id = ? AND user_id = ?",
                    meal_short,
                    meal_long,
                    photo_path,
                    meal_id,
                    session["user_id"],
                )
            flash("Meal updated successfully.", "success")
            return redirect(url_for("index"))


@app.route("/delete_meal", methods=["POST"])
@login_required
def delete_meal():
    """Delete a meal."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        meal_id = request.form.get("meal_id")
        if not meal_id:
            flash("Invalid meal.", "danger")
            return redirect(url_for("index"))

        # Check if photo exists and delete it
        result = db.execute("SELECT photo_path FROM diary WHERE id = ?", meal_id)
        delete_photo = result[0]['photo_path'] if result else None

        if delete_photo and os.path.exists(delete_photo):
            os.remove(delete_photo)

        db.execute("DELETE FROM diary WHERE id = ? AND user_id = ? AND date", meal_id, session["user_id"])

        flash("Meal deleted successfully.", "success")
        return redirect(url_for("index"))

@app.route("/replace_meal", methods=["POST"])
@login_required
def replace_meal():
    """Replace an existing meal entry"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        existing_meal_id = request.form.get("existing_meal_id")
        meal_short = request.form.get("meal_short")
        meal_long = request.form.get("meal_long")
        photo_path = request.form.get("photo_path")

        if not existing_meal_id or not meal_short:
            flash("No data found to replace.", "danger")
            return redirect(url_for("meal"))

        # Check if the old photo exists and delete it
        result = db.execute("SELECT photo_path FROM diary WHERE id = ?",int(existing_meal_id))
        old_photo_path = result[0]['photo_path'] if result else None

        if old_photo_path and os.path.exists(old_photo_path):
            os.remove(old_photo_path)

        # Update the existing meal entry in the diary table
        db.execute(
            "UPDATE diary SET short_descr = ?, long_descr = ?, photo_path = ? WHERE id = ?",
            meal_short,
            meal_long,
            photo_path,
            int(existing_meal_id)
        )

        flash("Meal successfully replaced.", "success")
        return redirect(url_for("index"))

