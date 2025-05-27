from django.db import models
from django.utils.timezone import now

class Member(models.Model):
    username = models.CharField(max_length=50)
    self_ig = models.CharField(max_length=50, blank=True, null=True)
    other_ig = models.CharField(max_length=50, blank=True, null=True)
    is_matched = models.BooleanField(default=False)
    notifications = models.JSONField(default=list)
    def __str__(self):
        return self.username

    def add_notification(self, text):
        self.notifications.append({'text': text, 'read': False, "timestamp": now().isoformat()})

    def unread_count(self):
        return sum(1 for n in self.notifications if not n.get('read', False))

    def mark_all_as_read(self):
        for n in self.notifications:
            n['read'] = True