from setuptools import setup, find_packages

setup(
    name="diagsoft",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flet>=0.22.0',
        'sqlalchemy>=2.0.0',
        'python-jose[cryptography]>=3.3.0',
        'passlib>=1.7.4',
        'python-multipart>=0.0.5',
        'python-dateutil>=2.8.2',
        'reportlab>=4.0.4',
        'matplotlib>=3.7.1',
        'bcrypt>=4.0.1',
        'pillow>=10.0.0',
        'pydantic>=2.0.0',
        'python-dotenv>=1.0.0',
        'werkzeug>=2.0.0'
    ],
    python_requires='>=3.7',
)