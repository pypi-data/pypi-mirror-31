from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    with open('README.md') as f:
        long_description = f.read()

setup(
    name='password_manager',
    version='0.1.0',
    description='A library for password manager for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/patarapolw/memorable_pwm',
    author='Pacharapol Withayasakpunt',  # Optional
    author_email='patarapolw@gmail.com',  # Optional
    keywords='password password-manager',
    packages=['password_manager'],
    install_requires=['pycryptodome'],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security',
        'Topic :: Security :: Cryptography'
    ],
    extras_require={
        'tests': ['pytest', 'pytest-readme'],
    }
)