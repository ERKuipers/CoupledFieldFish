# CoupledFieldFish
 
By Els Kuipers 28/6/2024 at Utrecht University

Using a .nc file entailing environmental variables, the barbel model can be run using the code in the following code repository: 
https://github.com/ERKuipers/CoupledFieldFish

Install Campo (https://campo.computationalgeography.org/)
And some packages 
- XUgrid (https://github.com/Deltares/xugrid) (for flexible mesh manipulation)
- XRarray (https://docs.xarray.dev/en/stable/) 
- Numpy (https://numpy.org/doc/)
- Pandas (https://pandas.pydata.org/docs/)

### SETTING UP MODEL:
Set up specific configurations using one of the configurations files in the 'input' folder. Please also check settings in the 'phenomena.py' script in the 'pre_processing' folder, 
which may be altered depending on whether a moving average is required.

### RUNNING THE MODEL: 
Using one of the files in the 'running' folder and changing the linking to the configurationsetting script you are using.

### EXPORTING THE OUTPUT: 
Exports are suggested in the same file where a model run is performed. When requiring specific data reduction from some properties, 
please consult the 'exporting.py' script in the 'post_processing' folder for your options. 

### VISUALISATION AND ANALYSIS:
Some datareduction visualisation and analysis scripts are suggested in the post_processing folder.
