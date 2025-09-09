from django.shortcuts import render
from .models import ScheduledClass, Section

DAYS_OF_WEEK = range(1, 7)   # Monday - Saturday
PERIODS = range(1, 9)        # Periods 1 - 8

def view_timetable(request):
    sections = Section.objects.all()
    selected_section_id = request.GET.get('section_id')
    table_rows = []

    # --- DEBUGGING STEP 1 ---
    print(f"\n[DEBUG] Request received. Selected Section ID: {selected_section_id}")

    if selected_section_id:
        scheduled_classes = ScheduledClass.objects.filter(section_id=selected_section_id).select_related(
            'subject', 'faculty', 'classroom'
        )

        # --- DEBUGGING STEP 2 ---
        print(f"[DEBUG] Classes found in database for section {selected_section_id}: {len(scheduled_classes)}")

        # Build timetable grid (day → period)
        temp_grid = {day: {period: None for period in PERIODS} for day in DAYS_OF_WEEK}
        for s_class in scheduled_classes:
            if s_class.day in temp_grid and s_class.period in temp_grid[s_class.day]:
                temp_grid[s_class.day][s_class.period] = s_class

        # Build rows (now day-wise, with periods as cells)
        for day in DAYS_OF_WEEK:
            row_data = {'day_number': day, 
                         'day_name': ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][day - 1],
                         'cells': []
                        }
            for period in PERIODS:
                row_data['cells'].append(temp_grid[day][period])
            table_rows.append(row_data)

        # --- DEBUGGING STEP 3 ---
        print(f"[DEBUG] Number of rows prepared for template: {len(table_rows)}")

    else:
        print("[DEBUG] No section ID selected. Sending empty page.")

    context = {
        'sections': sections,
        'selected_section_id': int(selected_section_id) if selected_section_id else None,
        'table_rows': table_rows,
        'day_headers': ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        'period_headers': [f"Period {p}" for p in PERIODS]
    }
    return render(request, 'scheduler/timetable_display.html', context)
