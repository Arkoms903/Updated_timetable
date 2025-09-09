from django.shortcuts import render
from .models import ScheduledClass, Section

DAYS_OF_WEEK = range(1, 7)   # Monday - Saturday
PERIODS = range(1, 9)        # Periods 1 - 8

def generate_period_times(start="08:30", duration=50, periods=8):
    from datetime import datetime, timedelta

    start_time = datetime.strptime(start, "%H:%M")
    result = []
    for i in range(periods):
        end_time = start_time + timedelta(minutes=duration)
        result.append((start_time.strftime("%H:%M"), end_time.strftime("%H:%M")))
        start_time = end_time
    return result

def view_timetable(request):
    sections = Section.objects.all()
    selected_section_id = request.GET.get('section_id')
    table_rows = []

    PERIOD_TIMES = generate_period_times(start="08:30", duration=50, periods=8)

    if selected_section_id:
        scheduled_classes = ScheduledClass.objects.filter(
            section_id=selected_section_id
        ).select_related('subject', 'faculty', 'classroom')

        # build grid
        temp_grid = {day: {p: None for p in range(1, 9)} for day in range(1, 7)}
        for s_class in scheduled_classes:
            temp_grid[s_class.day][s_class.period] = {
                "subject": s_class.subject,
                "faculty": s_class.faculty,
                "classroom": s_class.classroom,
                "start_time": PERIOD_TIMES[s_class.period - 1][0],
                "end_time": PERIOD_TIMES[s_class.period - 1][1],
            }

        for day in range(1, 7):
            row_data = {"day_name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][day-1],
                        "cells": []}
            for p in range(1, 9):
                row_data["cells"].append(temp_grid[day][p])
            table_rows.append(row_data)

    context = {
        "sections": sections,
        "selected_section_id": int(selected_section_id) if selected_section_id else None,
        "table_rows": table_rows,
        "period_headers": [
            f"Period {i+1} ({PERIOD_TIMES[i][0]} - {PERIOD_TIMES[i][1]})"
            for i in range(len(PERIOD_TIMES))
        ],
    }
    return render(request, "scheduler/timetable_display.html", context)
