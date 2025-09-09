<<<<<<< HEAD
# Django Timetable Generator 📅

This project is an automated timetable scheduling system built with **Django** and **Google OR-Tools**.  
It uses constraint satisfaction programming to generate valid weekly schedules for multiple sections, faculties, and classrooms based on predefined rules.

---

## ✨ Features

- **Constraint-Based Scheduling:** Automatically avoids conflicts for classrooms, faculties, and sections.  
- **Custom Rule Enforcement:**
  - Prevents sections from having classes for the same subject in consecutive periods.
  - Enforces faculty workload limits (e.g., a faculty member can teach a maximum of two distinct subjects).
- **Team Teaching Support:** Assign multiple faculty members to a single course (e.g., one for theory, one for tutorials).  
- **Web Interface:** Filterable timetable view by section.  
- **Django Admin Integration:** Manage subjects, sections, faculties, and classrooms easily.  

---

## 🛠️ Technology Stack

- **Backend:** Django  
- **Constraint Solver:** Google OR-Tools (CP-SAT Solver)  
- **Database:** SQLite (default, can be changed)  

---

## 🚀 How to Run Locally

1. **Clone the repository**

   ```bash
   git clone https://github.com/Sanjana023/timetable-scheduler.git
   cd timetable-scheduler

   ```

2. **Set Up Virtual Environment**
    *On Windows:*
    ```bash
        python3 -m venv env
        source env/bin/activate
    ```

3. **Install Dependencies**
    ```bash
       pip install -r requirements.txt
    ```

4. **Database Setup**
    ```bash
       # Apply database migrations
        python manage.py migrate

        # Create a superuser to access the admin panel
        python manage.py createsuperuser

    ```

## 🚀 How to Use

### Step 1: Run the Server & Enter Data
Start the server:
```bash
python manage.py runserver
 ```

Open http://127.0.0.1:8000/admin/

Log in with your superuser credentials.

Add data in this order:

1.Faculties

2.Sections

3.Classrooms

4.Subjects

5.Course Offerings (link subjects to sections, define weekly hours)

6.Faculty Assignments (assign teachers for Theory/Tutorials)

### Step 2: Generate the Timetable
```bash
python manage.py generate_timetable
 ```

### Step 3: View Results
Admin Panel: Check Scheduled Classes.

Frontend View: Open http://127.0.0.1:8000/timetable/
to view timetables in grid format.

Will change the UI later👍

=======
# Updated_timetable
>>>>>>> 9d19c642fa468efc764133c131552999a2749033
