from django.db import models


class BasicAddressAbstract(models.Model):
    """Abstract model for basic location information"""

    class Meta:
        abstract = True

    state = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    country_code = models.CharField(max_length=256, default="US")
    postal_code = models.CharField(max_length=5)


class Contact(BasicAddressAbstract):
    """Contact information"""

    class Meta:
        db_table = "contacts"
        unique_together = ("first_name", "last_name", "email")

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    linkedin_url = models.URLField(max_length=256)
    web_portfolio_url = models.URLField(max_length=256, null=True, blank=True)
    phone_number = models.CharField(max_length=12, blank=True)
    email = models.EmailField(max_length=256, blank=True)


class School(BasicAddressAbstract):
    """Holds locations for education records"""

    class Meta:
        db_table = "schools"

    name = models.CharField(max_length=256, unique=True)


class DegreeChoices(models.TextChoices):
    """Choice options for EducationHistory degree"""

    HIGH_SCHOOL = "High School Diploma"
    BACHELORS = "Bachelors"
    MASTERS = "Masters"
    PHD = "PhD"


class EducationHistory(models.Model):
    """Holds information regarding education history"""

    class Meta:
        db_table = "education_history"

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    degree = models.CharField(max_length=64, blank=True, choices=DegreeChoices.choices)
    major = models.CharField(max_length=64, blank=True)
    minor = models.CharField(max_length=64, blank=True)


class Company(BasicAddressAbstract):
    """Holds information regarding previous employers"""

    class Meta:
        db_table = "companies"

    company_name = models.CharField(max_length=256, unique=True)
    position = models.CharField(max_length=128, help_text="Employment title")


class Job(models.Model):
    """Holds information regarding prior work experience"""

    class Meta:
        db_table = "jobs"

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    @property
    def examples(self):
        return self.experiences.all()


class WorkExperience(models.Model):
    """Holds descriptions/examples of work history"""

    class Meta:
        db_table = "work_experiences"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="experiences")
    specification = models.CharField(max_length=64, help_text="basic grouping for type of work experience")
    description = models.TextField()
