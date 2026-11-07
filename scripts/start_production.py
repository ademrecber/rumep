"""Run Django preparation with runtime configuration, then replace with Gunicorn."""
import os
import subprocess
import sys


def main():
    # Database and object-storage credentials come only from Railway at runtime.
    # A failed migration must not start a partially prepared deployment.
    for command in ('migrate', 'collectstatic'):
        subprocess.run([sys.executable, 'manage.py', command, '--noinput'], check=True)
    os.execvp('gunicorn', [
        'gunicorn', 'rumep.wsgi:application',
        '--bind', f"0.0.0.0:{os.environ.get('PORT', '8080')}",
        '--access-logfile', '-', '--error-logfile', '-',
    ])


if __name__ == '__main__':
    main()
