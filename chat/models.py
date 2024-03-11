from django.db import models
from django.contrib.auth.models import User, AbstractUser, Group, Permission

class UserProfile(AbstractUser):
    is_active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name='user_profiles')
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='user_profiles',
        help_text='Specific permissions for this user.'
    )


class Room(models.Model):
    ROOM_TYPES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )

    name = models.CharField(max_length=255)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)

    def __str__(self):
        return self.name

class Message(models.Model):
    MESSAGE_STATUSES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    )

    content = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    status = models.CharField(max_length=10, choices=MESSAGE_STATUSES, default='sent')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} -> {self.timestamp}: {self.content}'