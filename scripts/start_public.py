"""Start the explicitly database-free public site; never mutate legacy storage."""
import os
import subprocess
import sys


def main():
    if not os.environ.get('SECRET_KEY'):
        raise RuntimeError('SECRET_KEY must be configured for public website signing.')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'rumep.public_settings'
    subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], check=True)
    os.execvp('gunicorn', ['gunicorn', 'rumep.public_wsgi:application',
                          '--bind', f"0.0.0.0:{os.environ.get('PORT', '8080')}",
                          '--access-logfile', '-', '--error-logfile', '-'])


if __name__ == '__main__':
    main()
