from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    likes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *arg, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*arg, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Page(models.Model):

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length = 128)
    url = models.URLField()
    views = models.IntegerField(default = 0)

    def __str__(self):
        return self.title

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # If url is not empty and doesn't start with http://
        # then prepend "http://".
        if url and not url.startswith("http://"):
            url = "http://" + url
            cleaned_data['url'] = url

            return cleaned_data

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # The additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    def __str__(self):
        return self.user.username



