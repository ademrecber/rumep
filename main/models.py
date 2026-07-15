from django.db import models

class RuxPdfComment(models.Model):
    name = models.CharField(max_length=100, verbose_name="İsim")
    message = models.TextField(verbose_name="Mesaj/Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tarih")
    is_approved = models.BooleanField(default=True, verbose_name="Onaylı mı?")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Rux PDF Yorumu"
        verbose_name_plural = "Rux PDF Yorumları"

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"
