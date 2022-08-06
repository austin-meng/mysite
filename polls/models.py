from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    
    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text



class User(models.Model):
    username = models.CharField('账号', max_length=16, unique=True)
    password = models.CharField('密码', max_length=16)
    email = models.EmailField('邮箱', unique=True)
    c_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['c_time']  # 元数据里定义用户按创建时间的反序排列，也就是最近的最先显示
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):  # 使用__str__帮助人性化显示对象信息
        return self.username