# top of file imports
import collections
from ortools.sat.python import cp_model
from datetime import datetime, timedelta

from .models import (
    CourseOffering, FacultyAssignment, Classroom, ScheduledClass,
    Section, Subject, Faculty
)

# --- Time & grid constants ---
DAYS = range(1, 7)
PERIODS = range(1, 9)

def generate_period_times(start="09:00", duration=45, periods=8):
    """Generate a dict mapping period numbers to (start_time, end_time) as time objects."""
    period_times = {}
    start_dt = datetime.strptime(start, "%H:%M")
    for i in range(1, periods + 1):
        end_dt = start_dt + timedelta(minutes=duration)
        period_times[i] = (start_dt.time(), end_dt.time())
        start_dt = end_dt
    return period_times


class TimetableORToolsSolver:
    def __init__(self, start_time="09:00", period_duration=45, periods_per_day=8):
        # load data
        self.all_sections = list(Section.objects.all())
        self.all_classrooms = list(Classroom.objects.all())
        self.all_faculties = list(Faculty.objects.all())

        # solver
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables = {}

        # generate period times and store on instance so methods can access it
        self.periods_count = periods_per_day
        self.period_times = generate_period_times(start=start_time, duration=period_duration, periods=periods_per_day)

    # ... keep your solve(), _prepare_class_requirements(), _create_variables(), _apply_constraints() as before ...

    def _save_results(self):
        """Saves the solved timetable from the solver memory into the ScheduledClass database model."""
        ScheduledClass.objects.all().delete()  # Clear old schedule first
        new_classes = []
        req_lookup = {r["id"]: r for r in self.class_requirements}

        for (req_id, day, period, room_id), var in self.variables.items():
            if self.solver.Value(var) == 1:
                req_data = req_lookup[req_id]

                # Get start/end times from the instance mapping
                start_time, end_time = self.period_times[period]

                new_classes.append(ScheduledClass(
                    day=day,
                    period=period,
                    classroom_id=room_id,
                    faculty=req_data["faculty"],
                    subject=req_data["subject"],
                    section=req_data["section"],
                    class_type=req_data["class_type"],
                    start_time=start_time,
                    end_time=end_time
                ))

        ScheduledClass.objects.bulk_create(new_classes)
        print(f"✅ Successfully saved {len(new_classes)} scheduled classes to database.")
