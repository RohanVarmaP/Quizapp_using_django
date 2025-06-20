# Generated by Django 5.2.3 on 2025-06-18 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_rename_attendedtablequiz_attendedquiztable_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiztable',
            name='questions',
            field=models.ManyToManyField(through='quiz.QuestionsinQuizTable', to='quiz.questiontable'),
        ),
        migrations.AlterUniqueTogether(
            name='attendedquiztable',
            unique_together={('user', 'quiz')},
        ),
        migrations.AlterUniqueTogether(
            name='markstable',
            unique_together={('user', 'quiz')},
        ),
    ]
