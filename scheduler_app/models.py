from django.db import models
from django.forms import ValidationError


class Faculty(models.Model):
    class Role(models.TextChoices):
        ASSISTANT_PROFESSOR = 'AP', 'Assistant Professor'
        ASSOCIATE_PROFESSOR = 'ASP', 'Associate Professor'
        PROFESSOR = 'P', 'Professor'

    name = models.CharField(max_length=100, unique=True)
    role = models.CharField(
        max_length=3,
        choices=Role.choices,
        default=Role.ASSISTANT_PROFESSOR
    )
    min_hours_per_week = models.PositiveIntegerField(default=0)
    max_hours_per_week = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

    class Meta:
        verbose_name_plural = "Faculties"


class Classroom(models.Model):
    name = models.CharField(max_length=50, help_text="eg., Room 101, Lab A")
    capacity = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=12, help_text="eg., Section A, Section B")

    def __str__(self):
        return self.name


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code}: {self.name}"


class CourseOffering(models.Model):
    """Defines a single course offering for a section."""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    required_theory_hours = models.PositiveIntegerField(default=3)
    required_tutorial_hours = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('subject', 'section')

    def __str__(self):
        return f"{self.subject.name} for {self.section.name}"


class FacultyAssignment(models.Model):
    class ClassTypeResponsibility(models.TextChoices):
        ALL = 'ALL', 'All Classes'
        THEORY_ONLY = 'THEORY', 'Theory Only'
        TUTORIAL_ONLY = 'TUTORIAL', 'Tutorial Only'

    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="faculty_assignments"
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="course_assignments"
    )
    responsibility = models.CharField(
        max_length=20,
        choices=ClassTypeResponsibility.choices,
        default=ClassTypeResponsibility.ALL,
    )

    class Meta:
        unique_together = ('course_offering', 'faculty')

    def __str__(self):
        return f"{self.faculty.name} teaches {self.responsibility} for {self.course_offering}"

    def clean(self):
        """At most 2 distinct subjects per faculty."""
        super().clean()
        if self.faculty:
            assigned_offerings = FacultyAssignment.objects.filter(
                faculty=self.faculty
            ).exclude(pk=self.pk)

            distinct_subject_ids = set(
                assigned_offerings.values_list('course_offering__subject_id', flat=True)
            )
            is_new_subject = self.course_offering.subject_id not in distinct_subject_ids
            current_subject_count = len(distinct_subject_ids)

            if is_new_subject and current_subject_count >= 2:
                raise ValidationError(
                    f"Faculty '{self.faculty}' already has {current_subject_count} subjects."
                )


class ScheduledClass(models.Model):
    class ClassType(models.TextChoices):
        THEORY = 'THEORY', 'Theory'
        TUTORIAL = 'TUTORIAL', 'Tutorial'

    DAYS_OF_WEEK = [(i, f"Day {i}") for i in range(1, 7)]
    PERIODS = [(i, f"Period {i}") for i in range(1, 9)]

    day = models.IntegerField(choices=DAYS_OF_WEEK)
    period = models.PositiveIntegerField()
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name="scheduled_classes")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="scheduled_classes")
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="scheduled_classes")
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, related_name="scheduled_classes")
    class_type = models.CharField(max_length=10, choices=ClassType.choices)

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = [
            ('day', 'period', 'classroom'),
            ('day', 'period', 'section'),
            ('day', 'period', 'faculty'),
        ]
        ordering = ['day', 'period', 'section']

    def __str__(self):
        return f"Day {self.day}, Period {self.period}: {self.section} - {self.subject.code} ({self.faculty.name})"
