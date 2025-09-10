import collections
from ortools.sat.python import cp_model
from datetime import datetime, timedelta

from .models import (
    CourseOffering, FacultyAssignment, Classroom, ScheduledClass,
    Section, Subject, Faculty
)

DAYS = range(1, 7)
PERIODS = range(1, 9)


def generate_period_times(start="10:00", duration=50, periods=8):
    """Generate dict of period -> (start,end) time."""
    period_times = {}
    start_dt = datetime.strptime(start, "%H:%M")
    for i in range(1, periods + 1):
        end_dt = start_dt + timedelta(minutes=duration)
        period_times[i] = (start_dt.time(), end_dt.time())
        start_dt = end_dt
    return period_times


class TimetableORToolsSolver:
    def __init__(self, start_time="10:00", period_duration=50, periods_per_day=8):
        self.all_sections = list(Section.objects.all())
        self.all_classrooms = list(Classroom.objects.all())
        self.all_faculties = list(Faculty.objects.all())

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables = {}

        self.periods_count = periods_per_day
        self.period_times = generate_period_times(
            start=start_time,
            duration=period_duration,
            periods=periods_per_day
        )

        # prepared later
        self.class_requirements = []
        self.class_requirements_lookup = {}

    def _prepare_class_requirements(self):
        """Build requirements list from CourseOfferings and FacultyAssignments."""
        # TODO: fill this as per your logic
        # Example entry:
        # self.class_requirements = [
        #   {"id": 1, "faculty": fac, "subject": subj, "section": sec,
        #    "class_type": "THEORY"}
        # ]
        self.class_requirements_lookup = {r["id"]: r for r in self.class_requirements}

    def _apply_faculty_hour_constraints(self):
        """Ensure faculty hours follow their role limits."""
        for faculty in self.all_faculties:
            assigned_vars = [
                var for (req_id, day, period, room_id), var in self.variables.items()
                if self.class_requirements_lookup[req_id]["faculty"].id == faculty.id
            ]

            if not assigned_vars:
                continue

            total_hours = sum(assigned_vars)

            min_h = faculty.min_hours_per_week or 0
            max_h = faculty.max_hours_per_week or 1000

            self.model.Add(total_hours >= min_h)
            self.model.Add(total_hours <= max_h)

    def _apply_constraints(self):
        """Add all timetable constraints."""
        # existing constraints here...
        self._apply_faculty_hour_constraints()

    def _save_results(self):
        ScheduledClass.objects.all().delete()
        new_classes = []
        req_lookup = {r["id"]: r for r in self.class_requirements}

        for (req_id, day, period, room_id), var in self.variables.items():
            if self.solver.Value(var) == 1:
                req_data = req_lookup[req_id]
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
        print(f"✅ Saved {len(new_classes)} classes.")
