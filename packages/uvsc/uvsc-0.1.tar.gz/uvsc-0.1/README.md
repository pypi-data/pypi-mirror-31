# Installing a Release of pyUVSC

- todo

# Setting up a development environment for pyUVSC 

- Install Python:
https://www.python.org/downloads/windows/
Aquire the latest release of Python 3.x - 64-bit for Windows and install.
Make sure to install pip in the options.

- Use pip to install pypiwin32 and sphinx

- Install Eclipse (for Java Developers) 
https://www.eclipse.org/downloads/download.php?file=/oomph/epp/oxygen/R2/eclipse-inst-win64.exe
Oxygen.2 has been used for this document.

- Install PyDev plugin in Eclipse
http://www.pydev.org
    - Launch Eclipse.
    - Open __Help > Install New Software...__ menu
    - Add a site with the following URL: http://www.pydev.org/updates
    - Select the site and install __PyDev for Eclipse__

- Checkout this repository
- Switch to the Eclipse Workspace the project should live in.
- Create a new __PyDev Project__ named __PyUSVC__
- Project Type should be __Python__, Grammar Version = 3.6, __Add project directory to the PYTHONPATH__ 
If your interpreter is not set up you can use the auto setup here.
  
- Now add the source from the repository folder using: __New > Link to Existing Source...__ and add the folders /src and /test in two steps.

# Build documentation
- Browse to the sphinx directory and run: __make html__
- Documentation will be output to ./sphinx/build/html

