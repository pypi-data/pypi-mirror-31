from setuptools import setup

long_description = open("README.md").read()

setup(
    name="onesignal-notifications",
    version="0.1.0",
    url="https://github.com/Lanseuo/onesignal-notifications",
    description="OneSignal API Wrapper for Python",
    long_description=long_description,
    license="MIT",
    author="Lucas Hild",
    author_email="contact@lucas-hild.de",
    packages=["onesignal"],
    install_requires=["requests"]
)
