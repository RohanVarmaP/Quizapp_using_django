from django.contrib import admin
from .models import QuizTable,RoleTable,UserTable,MarksTable,QuestionTable,UserAnswerTable,QuestionsinQuizTable,AttendedQuizTable
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class CustomUserAdmin(BaseUserAdmin):
    model = UserTable
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(UserTable, CustomUserAdmin)
admin.site.register(RoleTable)
admin.site.register(QuizTable)
admin.site.register(QuestionTable)
admin.site.register(QuestionsinQuizTable)
admin.site.register(MarksTable)
admin.site.register(UserAnswerTable)
admin.site.register(AttendedQuizTable)
