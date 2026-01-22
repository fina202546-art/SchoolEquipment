from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', '管理者'),
        ('student', '学生'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='利用区分'
    )


class Equipment(models.Model):
    STATUS_CHOICES = [
        ('available', '利用可能'),
        ('borrowed', '貸出中'),
        ('damaged', '故障中'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name='備品名'
    )
    serial = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='管理番号'
    )
    description = models.TextField(
        verbose_name='機器の詳細説明'
    )
    condition = models.TextField(
        verbose_name='現在の状態'
    )
    status = models.CharField(
        max_length=20,
        default='available',
        choices=STATUS_CHOICES,
        verbose_name='在庫状況'
    )
    image = models.ImageField(
        upload_to='equipment_pics/',
        null=True,
        blank=True,
        verbose_name='画像'
    )

    def __str__(self):
        return self.name


class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '承認待ち'),
        ('approved', '承認済み'),
        ('rejected', '却下'),
        ('returned', '返却済み') ,
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        verbose_name='備品'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='申請者'
    )
    date_requested = models.DateTimeField(
        auto_now_add=True,
        verbose_name='申請日'
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name='承認有無'
    )
    status = models.CharField(
        max_length=20,
        default='pending',
        choices=STATUS_CHOICES,
        verbose_name='申請状況'
    )
    reason = models.TextField(
        null=True,
        blank=True
    ) 

    def __str__(self):
        return f"{self.equipment} - {self.student}"
