from setuptools import setup, find_packages

setup(
    name="Fantasio",  # Nom du package
    version="0.1.0",  # Version initiale
    packages=find_packages(),  # Recherche automatiquement les modules
    description="Fantasio, normalization tool for SPIRou .fits file",
    author="Lisa Drouglazet",
    author_email="lisa.drouglazet@univ-grenoble-alpes.fr",
    python_requires=">=3.6",  # Version minimale de Python
)
