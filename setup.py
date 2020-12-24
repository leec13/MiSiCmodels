import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MiSiCmodels", # Replace with your own username
    version="0.3.7",
    author="L.Espinosa",
    author_email="leonespcast@gmail.com",
    description="Microbe segmentation in dense colonies graphical interface using Napari with models selection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://imm.cnrs.fr",
    #packages=setuptools.find_packages(),
    packages=['MiSiCmodels'],
    package_dir={'MiSiCmodels': 'MiSiCmodels'},
    py_modules = ['utils', 'gui_utils'],
    include_package_data=True,
    install_requires=[
        'PyQt5',
        'napari==0.4.0',
        'magicgui',
        'tiffile',
        'MiSiC @ git+https://github.com/pswapnesh/MiSiC.git'
    ],
    #package_data={"": ["*.png"],"MiSiCgui": ["images/*.png"]},
    #data_files=[('images', ['images/screen1.png'])],
    dependency_links=['MiSiC @ git+https://github.com/pswapnesh/MiSiC.git'],
    entry_points = {
        'console_scripts': ['MODELS=MiSiCmodels.MiSiCgui_by_model:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
#upddate2, , 'models.*'