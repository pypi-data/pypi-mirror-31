import os
import sys
from setuptools import setup


def main():
        if float(sys.version[:3])<2.7 or float(sys.version[:3])>=2.8:
                sys.stderr.write("CRITICAL: Python version must be 2.7!\n")
                sys.exit(1)

        setup(name="IRTools",
              version="1.1.4.8",
              description="a computational toolset for detection and analysis of intron retention from RNA-Seq libraries",
              author='Zhouhao Zeng',
              author_email='zzhlbj23@gwmail.gwu.edu',
              url='https://github.com/zhouhaozeng/IRTools/',
              package_dir={'IRTools' : 'IRTools'},
              packages=['IRTools'],   
              package_data={'IRTools': ['data/*.gtf']},
              include_package_data=True,
              scripts=['bin/IRTools'],
              classifiers=[
                      'Development Status :: 4 - Beta',
                      'Environment :: Console',
                      'Intended Audience :: Developers',
                      'Intended Audience :: Science/Research',              
                      'License :: OSI Approved :: GNU General Public License (GPL)',
                      'Operating System :: MacOS :: MacOS X',
                      'Operating System :: POSIX',
                      'Topic :: Scientific/Engineering :: Bio-Informatics',
                      'Programming Language :: Python',
                      ],
              install_requires=[
                      'numpy',
                      'scipy',
                      'pandas',
                      'networkx',
                      'HTSeq==0.6.1',
                      'pysam==0.7.6'],
              )

if __name__ == '__main__':
        main()
