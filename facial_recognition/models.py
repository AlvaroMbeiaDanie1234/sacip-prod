from django.db import models
import json


class Suspect(models.Model):
    """
    Model representing a suspect with facial data.
    """
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    nid = models.CharField(max_length=50, blank=True, null=True)
    dangerous_level = models.CharField(max_length=50, blank=True, null=True)
    dangerous_color = models.CharField(max_length=20, blank=True, null=True)
    photo_paths = models.TextField(blank=True, null=True)  # JSON string of photo paths
    embeddings = models.TextField(blank=True, null=True)  # JSON string of face embeddings
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_photo_paths(self, paths):
        """Store photo paths as JSON string."""
        self.photo_paths = json.dumps(paths)

    def get_photo_paths(self):
        """Retrieve photo paths from JSON string."""
        if self.photo_paths:
            return json.loads(self.photo_paths)
        return []

    def set_embeddings(self, embeddings):
        """Store embeddings as JSON string."""
        self.embeddings = json.dumps(embeddings)

    def get_embeddings(self):
        """Retrieve embeddings from JSON string."""
        if self.embeddings:
            return json.loads(self.embeddings)
        return []

    def __str__(self):
        return f"{self.full_name} ({self.nickname})" if self.nickname else self.full_name


class CameraFeed(models.Model):
    """
    Model representing a camera feed for facial recognition.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.location}"


class RecognitionResult(models.Model):
    """
    Model representing a facial recognition result.
    """
    id = models.AutoField(primary_key=True)
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE)
    camera_feed = models.ForeignKey(CameraFeed, on_delete=models.CASCADE)
    similarity_score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    frame_data = models.TextField(blank=True, null=True)  # Base64 encoded frame

    def __str__(self):
        return f"Recognition of {self.suspect} at {self.timestamp}"


class Alert(models.Model):
    """
    Model representing an alert generated when a suspect is identified.
    """
    ALERT_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    id = models.AutoField(primary_key=True)
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE)
    camera_feed = models.ForeignKey(CameraFeed, on_delete=models.CASCADE)
    similarity_score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    alert_level = models.CharField(max_length=10, choices=ALERT_LEVEL_CHOICES, default='medium')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"Alert: {self.suspect} identified at {self.camera_feed} (Score: {self.similarity_score})"
        
    def save(self, *args, **kwargs):
        # Set alert level based on similarity score and suspect danger level
        if not self.alert_level:
            if self.similarity_score >= 0.5:
                self.alert_level = 'high'
            elif self.similarity_score >= 0.0:
                self.alert_level = 'medium'
            elif self.similarity_score >= -0.10:
                self.alert_level = 'low'
            else:
                # Very low similarity, shouldn't create alert
                pass
                
        super().save(*args, **kwargs)