# MCQ Exam System

A comprehensive online examination platform for multiple choice questions built with Django.

## 🚀 Features

### Core Functionality
- **Role-based Access Control**: Admin, Examiner, and Examinee roles
- **Exam Management**: Create, schedule, and manage exams
- **Question Upload**: Bulk upload questions via CSV files
- **Timed Examinations**: Fixed time limits with countdown timer
- **Auto-submission**: Automatic submission when time expires
- **Results Management**: Publish/unpublish results control

### User Experience
- **Beautiful UI**: Modern, responsive design with Bootstrap 5
- **Real-time Updates**: Live countdown timers and progress tracking
- **Smart Navigation**: Role-based landing pages and signup flow
- **Exam History**: Track performance and view past results
- **Email Verification**: Secure user registration process

### Technical Features
- **5-Option Questions**: Support for A, B, C, D, E choices
- **CSV Import**: Easy question management via spreadsheet upload
- **Session Management**: Secure exam sessions with auto-save
- **Timezone Support**: Proper timezone handling for global users
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🛠️ Technology Stack

- **Backend**: Django 5.0.6
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentication**: Django Allauth
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Icons**: Font Awesome
- **Charts**: Chart.js

## 📋 Requirements

- Python 3.8+
- Django 5.0.6
- Django Allauth
- Bootstrap 5
- Font Awesome

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/mcq-exam-system.git
   cd mcq-exam-system
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Open your browser and go to `http://127.0.0.1:8000`

## 👥 User Roles

### Admin
- Full system access
- User management
- All examiner and examinee permissions

### Examiner
- Create and manage exams
- Upload questions via CSV
- Set exam schedules and time limits
- View and publish results
- Track student performance

### Examinee
- Join exams with unique codes
- Take timed examinations
- View results (when published)
- Track exam history

## 📊 CSV Question Format

Upload questions using CSV files with the following format:

| question | option_1 | option_2 | option_3 | option_4 | option_5 | correct_answer |
|----------|----------|----------|----------|----------|----------|----------------|
| What is Python? | Programming language | Database | OS | Browser | Editor | 1 |
| Django is a? | Framework | Language | Database | Server | IDE | 1 |

**Note:** `correct_answer` should be a number from 1-5 corresponding to the correct option.

## 🎯 Usage

### For Examiners
1. Sign up as an Examiner
2. Create a new exam
3. Upload questions via CSV
4. Set exam schedule and duration
5. Share exam code with students
6. Monitor submissions and publish results

### For Examinees
1. Sign up as an Examinee
2. Use exam code to join an exam
3. Wait for exam to start (if scheduled)
4. Answer questions within time limit
5. Submit exam
6. View results (when published by examiner)

## 🔧 Configuration

### Timezone Settings
The system is configured for Asia/Dhaka timezone. To change:

1. Edit `config/settings.py`:
   ```python
   TIME_ZONE = 'Your/Timezone'
   ```

2. Restart the server

### Email Configuration
Configure email settings in `config/settings.py` for email verification:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-host'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email'
EMAIL_HOST_PASSWORD = 'your-password'
```

## 📱 Screenshots

*Add screenshots of your application here*

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the responsive UI components
- Font Awesome for the beautiful icons

## 📞 Support

If you have any questions or need help, please:
- Open an issue on GitHub
- Contact the author via email
- Check the documentation

---

**Made with ❤️ using Django**
