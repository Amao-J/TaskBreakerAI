from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from collections import Counter
from django.utils.timezone import now
from datetime import timedelta


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if email is None:
            raise TypeError('Users must have an email.')
    
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password, **kwargs):
        user = self.create_user(email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user
  
    
class User(AbstractBaseUser, PermissionsMixin):
    date_joined = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    email = models.EmailField(db_index=True, unique=True, null=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    profile_image = models.ImageField(upload_to="uploads", blank=False, null=False, default='/staticfiles/images/defaultuserimage.png')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    
    
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True
    )
    
    
    def get_full_name(self):
        return f' {self.first_name}  {self.last_name}'

    USERNAME_FIELD = 'email'
    objects = UserManager()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
        


class Preferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences') 
    roles = models.CharField(max_length=50, choices=(
        ('Freelancer', 'Freelancer'),
        ('Remote Worker', 'Remote Worker'),
        ('Business Owner', 'Business Owner'),
        ('Student', 'Student'),
        ('Hobbyist', 'Hobbyist')
    ), default="Hobbyist")
    
    time_of_day = models.CharField(max_length=50, choices=(
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Evening', 'Evening')
    ), default="")
    
    sound = models.CharField(max_length=40, choices=(
        ('Quiet','Queit'),
        ('Background music','Background music')
        ))
    
    
    class Meta:
        verbose_name = "Preference"
        verbose_name_plural = "Preferences"
        
    def update_preferences(self, roles=None, time_of_day=None, sound=None):
        
        if roles:
            self.roles = roles
        if time_of_day:
            self.time_of_day = time_of_day
        if sound:
            self.sound = sound
        self.save()
    
    
class Goals(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    description = models.CharField(max_length=250, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    
    class Meta:
        verbose_name = "Goal"
        verbose_name_plural = "Goals"
    
    

    
     
    
    def __str__(self):
        return self.description
    
class Subtasks(models.Model):
    tasks = models.ForeignKey(Goals, on_delete=models.CASCADE, related_name="tasks")
    description = models.CharField(max_length=250, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    
    class Meta:
        verbose_name = "Subtask"
        verbose_name_plural = "Subtasks"

    def __str__(self):
        return f"Subtask: {self.description} for Goal: {self.tasks.description}"
  
    
    
class Dashboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard') 
    goals = models.ManyToManyField(Goals, related_name='dashboards')  
    subtasks = models.ManyToManyField(Subtasks, related_name='dashboards')
    updated = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"Dashboard for {self.user.email if self.user and self.user.email else 'Unknown User'}"
    
    def calculate_completed_percentage(self):
       
        total_goals = self.goals.count()
        completed_goals = self.goals.filter(completed=True).count()

        
        total_subtasks = self.subtasks.count()
        completed_subtasks = self.subtasks.filter(completed=True).count()

        
        goal_percentage = (completed_goals / total_goals) * 100 if total_goals > 0 else 0
        subtask_percentage = (completed_subtasks / total_subtasks) * 100 if total_subtasks > 0 else 0

        
        return {
            'goal_percentage': goal_percentage,
            'subtask_percentage': subtask_percentage,
        }
        
    def tasks_completed(self, period='day'):
        if period == 'day':
            start_time = timezone.now() - timedelta(days=1)
        elif period == 'week':
            start_time = timezone.now() - timedelta(weeks=1)
        else:
            return 0
        
        return self.subtasks.filter(completed=True, completed_at__gte=start_time).count()
    
    def missed_or_overdue_goals(self):
        now = timezone.now()
        return self.goals.filter(completed=False, due_date__lt=now)
    
    def goal_progress(self):
        completed_goals = self.goals.filter(completed=True).count()
        total_goals = self.goals.count()
        return (completed_goals / total_goals) * 100 if total_goals > 0 else 0
    
    
    def task_completion_rate(self):
        total_tasks = self.subtasks.count()
        completed_tasks = self.subtasks.filter(completed=True).count()
        return (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    
    
    def overdue_tasks_grouped_by_goals(self):
   
        now = timezone.now()
        overdue_subtasks = self.subtasks.filter(completed=False, tasks__due_date__lt=now)

        grouped_tasks = {}
        for subtask in overdue_subtasks:
            goal = subtask.tasks  
            if goal not in grouped_tasks:
                grouped_tasks[goal] = []
            grouped_tasks[goal].append(subtask)

        return grouped_tasks
    
    

    def top_productivity_hours(self):
        completed_tasks = self.subtasks.filter(completed=True)
        task_hours = [subtask.completed_at.hour for subtask in self.subtasks.filter(completed=True) if subtask.completed_at]

        if not task_hours:
            return {"message": "No completed tasks to analyze."}

        hour_counts = Counter(task_hours)
        max_count = max(hour_counts.values())

        return {
            "top_hours": [hour for hour, count in hour_counts.items() if count == max_count],
            "task_count": max_count,
        }



    
    
    
    
class BlockedSite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField(max_length=200)
    duration = models.IntegerField(default=60)
    blocked_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def expiration(self):
        return self.blocked_at + timedelta(minutes=int(self.duration))

    def __str__(self):
        return f"{self.url} blocked for {self.duration} minutes"   
   


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Dashboard.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.dashboard.save(update_fields=['updated'])
    
    