import setuptools

with open("README.md", "r") as fh:
        long_description = fh.read()

        setuptools.setup(
                name="nubs01",
                version="0.0.1",
                author="Brandies Autonomous Robotics Lab",
                author_email="robotics@brandeis.edu",
                description="Brandeis Automomous Robotics Lab Pupper Robot Software",
                long_description=long_description,
                long_description_content_type="text/markdown",
                url="https://github.com/nubs01/PupperPy",
                packages=setuptools.find_packages(),
                package_data={'pupperpy': ['Controller/icons/*.png',
                                           'resources/*.service',
                                           'resources/*.conf']},
                classifiers=[
                            "Programming Language :: Python :: 3",
                            "License :: OSI Approved :: MIT License",
                            "Operating System :: OS Independent",
                        ],
                python_requires='>=3.6',
        )
