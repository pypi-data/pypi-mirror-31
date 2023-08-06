from setuptools import setup, find_packages

setup(
    name='odoo-cli',
    version='1.0',
    description='CLI Tool for Odoo11...',
    license='MIT',
    url='https://github.com/ahmed-girach/odoo-cli',
    author='Ahmed Girach',
    author_email='ahmedkhatri6@gmail.com',
    keywords=['odoo11', 'python3', 'cli'],
    classifiers=[],
    packages=find_packages(exclude=[]),
    python_requires='>=3',
)
