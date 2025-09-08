from django import forms
from django.db import transaction
from .models import Exam, Question, Choice


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'duration_minutes', 'start_time', 'end_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class QuestionUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with columns: question, option_1, option_2, option_3, option_4, option_5, correct_answer',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )


class QuestionEditForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuestionWithChoicesForm(forms.Form):
    """Form for editing a question with its choices"""
    question_text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Question Text'
    )
    order = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Question Order'
    )
    
    # Choice fields
    choice_1_text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Choice 1'
    )
    choice_1_correct = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Correct'
    )
    
    choice_2_text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Choice 2'
    )
    choice_2_correct = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Correct'
    )
    
    choice_3_text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Choice 3'
    )
    choice_3_correct = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Correct'
    )
    
    choice_4_text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Choice 4'
    )
    choice_4_correct = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Correct'
    )
    
    choice_5_text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Choice 5'
    )
    choice_5_correct = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Correct'
    )
    
    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)
        
        if self.question:
            # Pre-populate form with existing data
            self.fields['question_text'].initial = self.question.text
            self.fields['order'].initial = self.question.order
            
            # Pre-populate choices
            choices = list(self.question.choices.all().order_by('id'))
            for i in range(1, 6):
                if i <= len(choices):
                    self.fields[f'choice_{i}_text'].initial = choices[i-1].text
                    self.fields[f'choice_{i}_correct'].initial = choices[i-1].is_correct
                else:
                    # Empty choices for new ones
                    self.fields[f'choice_{i}_text'].initial = ''
                    self.fields[f'choice_{i}_correct'].initial = False
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check that at least one choice is marked as correct
        correct_choices = []
        for i in range(1, 6):
            if cleaned_data.get(f'choice_{i}_correct') and cleaned_data.get(f'choice_{i}_text'):
                correct_choices.append(i)
        
        if not correct_choices:
            raise forms.ValidationError("At least one choice must be marked as correct.")
        
        return cleaned_data
    
    def save(self):
        if not self.question:
            raise ValueError("Question instance is required to save.")
        
        # Update question
        self.question.text = self.cleaned_data['question_text']
        self.question.order = self.cleaned_data['order']
        self.question.save()
        
        # Update or create choices
        with transaction.atomic():
            # Delete existing choices
            self.question.choices.all().delete()
            
            # Create new choices
            for i in range(1, 6):
                choice_text = self.cleaned_data.get(f'choice_{i}_text', '').strip()
                if choice_text:  # Only create choice if text is provided
                    Choice.objects.create(
                        question=self.question,
                        text=choice_text,
                        is_correct=self.cleaned_data.get(f'choice_{i}_correct', False)
                    )
        
        return self.question
