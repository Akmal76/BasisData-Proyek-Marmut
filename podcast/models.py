from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Assuming you have a Podcast model
# Replace Podcast with your actual model name
class Podcast(models.Model):
    judul = models.CharField(max_length=100)
    genre = models.ManyToManyField(Genre)
    durasi = models.CharField(max_length=50)

    def __str__(self):
        return self.judul

class Episode(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    duration = models.IntegerField(default=0)

    def __str__(self):
        return self.title