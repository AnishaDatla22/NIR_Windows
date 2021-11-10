# DLP_Nanoevm
#sample code
Installation Steps:

#Install required packages/software

1. Install python3, git, pandas,numpy and matplotlib on your linux machine

#Install HIDAPI from https://github.com/trezor/cython-hidapi.git

2A.<br>
    $ sudo apt-get install python3-dev libusb-1.0-0-dev libudev-dev <br>
    $ sudo pip3 install --upgrade setuptools <br>
    $ sudo pip3 install hidapi<br>


OR

2B.<br> 
    $ sudo apt-get install python3-dev libusb-1.0-0-dev libudev-dev<br>
    $ git clone https://github.com/trezor/cython-hidapi.git<br>
    $ cd cython-hidapi<br>
    Initialize hidapi submodule:<br>
    $ git submodule update --init<br>
    Build cython-hidapi extension module:<br>
    $ python setup.py build <br>
    Install cython-hidapi module into your Python distribution:<br>
    $ sudo python setup.py install<br>
    
#Get the code

3. git clone https://github.com/AnishaDatla22/DLP_Nanoevm.git

#Run the code

4. sudo python3 main.py    



# nir_latest
