from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
# Register your models here.

from .models import UserProfile

class UserProfileCreationForm(forms.ModelForm):
	"""A form for creating new users. Includes all the required
	fields, plus a repeated password."""
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

	class Meta:
		model = UserProfile
		fields = ('email', 'full_name')

	def clean_password2(self):
		# Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

	def save(self, commit=True):
		# Save the provided password in hashed format
		user = super(UserProfileCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user

class UserProfileEditForm(forms.ModelForm):
	"""A form for updating users. Includes all the fields on
	the user, but replaces the password field with admin's
	password hash display field.
	"""
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = UserProfile
		fields = ('email', 'password', 'full_name' , 'is_admin' ,'is_active')

	def clean_password(self):
		return self.initial["password"]

class UserProfileAdmin(UserAdmin):
	# The forms to add and change user instances
	form = UserProfileEditForm
	add_form = UserProfileCreationForm

	# The fields to be used in displaying the User model.
	# These override the definitions on the base UserAdmin
	# that reference specific fields on auth.User.
	list_display = ('email', 'full_name', 'is_admin')
	list_filter = ('is_admin',)
	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		('Personal info', {'fields': ('full_name',)}),
		('Permissions', {'fields': ('is_admin',)}),
		# ('Important dates', {'fields': ('last_login',)}),
	)
	# add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
	# overrides get_fieldsets to use this attribute when creating a user.
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'full_name', 'password1', 'password2')}
		),
	)
	search_fields = ('email',)
	ordering = ('email',)
	filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(UserProfile, UserProfileAdmin)
# ... and, since we're not using Django's builtin permissions,
# unregister the Group model from admin.
#admin.site.unregister(Group)