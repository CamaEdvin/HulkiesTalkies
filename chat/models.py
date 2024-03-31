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

    name = models.CharField(max_length=255, verbose_name='name')
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, verbose_name='room_type')

    def __str__(self):
        return self.name
    
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'room_type': self.room_type,
        }


class Message(models.Model):
    MESSAGE_STATUSES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    )

    content = models.TextField(default='', verbose_name='content')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='sender')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True, verbose_name='recipient')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages', verbose_name='room')
    status = models.CharField(max_length=10, choices=MESSAGE_STATUSES, default='sent', verbose_name='status')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='timestamp')

    def __str__(self):
        return f'{self.sender} -> {self.timestamp}: {self.content}'
    
    def as_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'sender': self.sender.get_full_name() if self.sender else None,
            'recipient': self.recipient.get_full_name() if self.recipient else None,
            'room': self.room.name if self.room else None,
            'status': self.status,
            'timestamp': self.timestamp,
        }

    class Meta:
        ordering = ["timestamp"]


class RoomMember(models.Model):
    users = models.ManyToManyField(User, verbose_name='users')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='room')

    def __str__(self):
        return str(self.room.name) if self.room else ''
    
    def as_dict(self):
        return {
            'id': self.id,
            'users': [user.get_full_name() for user in self.users.all()],
            'room': self.room.name if self.room else None,
        }

