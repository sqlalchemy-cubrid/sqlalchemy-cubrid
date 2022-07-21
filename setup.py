from setuptools import setup

setup(
    name="sqlalchemy_cubrid",
    version="0.0.1",
    description="Cubrid dialect for SQLAlchemy",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="SQLAlchemy Cubrid",
    author="Yeongseon Choe, Gyeongjun Paik",
    author_email="yeongseon.choe@gmail.com, paikend@gmail.com",
    license="MIT",
    packages=["sqlalchemy_cubrid"],
    include_package_data=True,
    tests_require=["pytest >= 2.5.2"],
    install_requires=[
        "sqlalchemy",
        "CUBRID-Python",
    ],
    entry_points={
        "sqlalchemy.dialects": [
            "cubrid = sqlalchemy_cubrid.dialect:CubridDialect",
        ]
    },
)
