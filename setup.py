from setuptools import setup

setup(
    name='mcserverapi',
    version='1.0.3',
    packages=['mcserverapi'],
    url='https://github.com/TeamNightSky/MCServerWrapper',
    license='GNU License',
    author='Pixymon',
    author_email='nlarsen23.student@gmail.com',
    description='Integratable API for Local Minecraft Servers',
    install_requires=['requests', 'psutil']
)
