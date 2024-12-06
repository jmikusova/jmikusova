# Meal Tracker
#### Video Demo:  <URL HERE>
#### Description:

>This is my final project for CS50 Introduction to Computer Sciense course.

A simple web application that allows users to log, edit, and view meals for different days. Users can add meals by selecting the type (e.g., breakfast, lunch, dinner, snack), provide descriptions, upload photos, and view an overview of their meals over multiple weeks.

---
## Features

- **Meal Logging**: Add meals for different meal types (breakfast, lunch, dinner, snack) with short descriptions, long notes, and photos.
- **Meal Editing**: Edit existing meals by updating descriptions and replacing photos.
- **Date-Specific Entries**: Record meals for the current or previous dates.
- **Weekly Overview**: View all meals logged for the week in a tabular format.
- **Meal Replacement**: If a meal for the same day and meal type already exists, users are warned and can choose to replace the existing meal.
- **Meal Deleting**: Delete existing meals if desired.

---
## Usage

### Adding a New Meal for current date
1. Navigate to the "Meal Log" page.
2. Select a meal type.
3. Enter a short description, optional long description, and upload a photo if desired.
4. Save the meal.

### Viewing or Editing Existing Meals
- View logged meals on the home page.
- Click on a meal to edit, update, or delete it.

### Logging Meals for Previous Dates
1. Click the "Add Meal" option on the home page for the corresponding date and meal type.
2. Follow the same steps as adding a new meal.

---

## Technologies Used

- **Flask**: Web framework for building the application.
- **SQLite**: Database to store user meal logs.
- **Jinja2**: Template engine used to render dynamic HTML pages.
- **HTML/CSS**: For structuring and styling the frontend.
- **JavaScript**: For some interactive features, such as image previews.
- **Bootstrap**: Frontend framework for responsive design.

---

## Project Structure

```plaintext
project/
├── static/             # Static files (CSS, JavaScript, Images)
├── templates/          # HTML templates
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── requirements.txt    # Project dependencies
├── database.db         # SQLite database (generated)
└── README.md           # Project documentation


