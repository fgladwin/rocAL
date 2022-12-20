# Copyright (c) 2022 Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import sys
import argparse
import platform
if sys.version_info[0] < 3:
    import commands
else:
    import subprocess

__author__ = "Kiriti Nagesh Gowda"
__copyright__ = "Copyright 2022, AMD ROCm Augmentation Library"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Kiriti Nagesh Gowda"
__email__ = "mivisionx.support@amd.com"
__status__ = "Shipping"

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('--directory', 	type=str, default='~/rocal-deps',
                    help='Setup home directory - optional (default:~/)')
parser.add_argument('--opencv',    	type=str, default='4.6.0',
                    help='OpenCV Version - optional (default:4.6.0)')
parser.add_argument('--protobuf',  	type=str, default='3.12.4',
                    help='ProtoBuf Version - optional (default:3.12.4)')
parser.add_argument('--rpp',   		type=str, default='0.98',
                    help='RPP Version - optional (default:0.98)')
parser.add_argument('--mivisionx',   		type=str, default='rocm-5.4.1',
                    help='MIVisionX Version - optional (default:rocm-5.4.1)')
parser.add_argument('--ffmpeg',    	type=str, default='yes',
                    help='FFMPEG V4.4.2 Installation - optional (default:yes) [options:yes/no]')
parser.add_argument('--reinstall', 	type=str, default='no',
                    help='Remove previous setup and reinstall - optional (default:no) [options:yes/no]')
parser.add_argument('--backend', 	type=str, default='HIP',
                    help='rocAL Dependency Backend - optional (default:HIP) [options:CPU/OCL/HIP]')
parser.add_argument('--rocm_path', 	type=str, default='/opt/rocm',
                    help='ROCm Installation Path - optional (default:/opt/rocm) - ROCm Installation Required')
args = parser.parse_args()

setupDir = args.directory
opencvVersion = args.opencv
ProtoBufVersion = args.protobuf
rppVersion = args.rpp
mivisionxVersion = args.mivisionx
ffmpegInstall = args.ffmpeg
reinstall = args.reinstall
backend = args.backend
ROCM_PATH = args.rocm_path

if "ROCM_PATH" in os.environ:
    ROCM_PATH = os.environ.get('ROCM_PATH')
print("\nROCm PATH set to -- "+ROCM_PATH+"\n")

if ffmpegInstall not in ('no', 'yes'):
    print(
        "ERROR: FFMPEG Install Option Not Supported - [Supported Options: no or yes]")
    exit()
if reinstall not in ('no', 'yes'):
    print(
        "ERROR: Re-Install Option Not Supported - [Supported Options: no or yes]")
    exit()
if backend not in ('OCL', 'HIP', 'CPU'):
    print(
        "ERROR: Backend Option Not Supported - [Supported Options: CPU or OCL or HIP]")
    exit()

# check ROCm installation
if os.path.exists(ROCM_PATH) and backend != 'CPU':
    print("\nROCm Installation Found -- "+ROCM_PATH+"\n")
    os.system('echo ROCm Info -- && '+ROCM_PATH+'/bin/rocminfo')
else:
    if backend != 'CPU':
        print("\nWARNING: ROCm Not Found at -- "+ROCM_PATH+"\n")
        print(
            "WARNING: Set ROCm Path with \"--rocm_path\" option for full installation [Default:/opt/rocm]\n")
        print("WARNING: Only OpenCV will be installed\n")
    ffmpegInstall = 'no'
    neuralNetInstall = 'no'
    rocalInstall = 'no'

# get platfrom info
platfromInfo = platform.platform()

# sudo requirement check
sudoLocation = ''
userName = ''
if sys.version_info[0] < 3:
    status, sudoLocation = commands.getstatusoutput("which sudo")
    if sudoLocation != '/usr/bin/sudo':
        status, userName = commands.getstatusoutput("whoami")
else:
    status, sudoLocation = subprocess.getstatusoutput("which sudo")
    if sudoLocation != '/usr/bin/sudo':
        status, userName = subprocess.getstatusoutput("whoami")

# Setup Directory for Deps
if setupDir == '~/rocal-deps':
    setupDir_deps = setupDir
else:
    setupDir_deps = setupDir+'/rocal-deps'

# setup directory path
deps_dir = os.path.expanduser(setupDir_deps)
deps_dir = os.path.abspath(deps_dir)

# setup for Linux
linuxSystemInstall = ''
linuxCMake = 'cmake'
linuxSystemInstall_check = ''
linuxFlag = ''
if "centos" in platfromInfo or "redhat" in platfromInfo:
    linuxSystemInstall = 'yum -y'
    linuxSystemInstall_check = '--nogpgcheck'
    if "centos-7" in platfromInfo or "redhat-7" in platfromInfo:
        linuxCMake = 'cmake3'
        os.system(linuxSystemInstall+' install cmake3')
elif "Ubuntu" in platfromInfo or os.path.exists('/usr/bin/apt-get'):
    linuxSystemInstall = 'apt-get -y'
    linuxSystemInstall_check = '--allow-unauthenticated'
    linuxFlag = '-S'
    if not "Ubuntu" in platfromInfo:
        platfromInfo = platfromInfo+'-Ubuntu'
elif os.path.exists('/usr/bin/zypper'):
    linuxSystemInstall = 'zypper -n'
    linuxSystemInstall_check = '--no-gpg-checks'
    platfromInfo = platfromInfo+'-SLES'
else:
    print("\nrocAL Setup on "+platfromInfo+" is unsupported\n")
    print("\nrocAL Setup Supported on: Ubuntu 20/22; CentOS 7/8; RedHat 7/8; & SLES 15-SP2\n")
    exit()

# rocAL Setup
print("\nrocAL Setup on: "+platfromInfo+"\n")

if userName == 'root':
    os.system(linuxSystemInstall+' update')
    os.system(linuxSystemInstall+' install sudo')

# Delete previous install
if os.path.exists(deps_dir) and reinstall == 'yes':
    os.system('sudo -v')
    os.system('sudo rm -rf '+deps_dir)
    print("\nrocAL Setup: Removing Previous Install -- "+deps_dir+"\n")

# Re-Install
if os.path.exists(deps_dir):
    print("\nrocAL Setup: Re-Installing Libraries from -- "+deps_dir+"\n")
    # opencv
    if os.path.exists(deps_dir+'/build/OpenCV'):
        os.system('sudo -v')
        os.system('(cd '+deps_dir+'/build/OpenCV; sudo ' +
                  linuxFlag+' make install -j8)')

    # ProtoBuf
    if os.path.exists(deps_dir+'/protobuf-'+ProtoBufVersion):
        os.system('sudo -v')
        os.system('(cd '+deps_dir+'/protobuf-'+ProtoBufVersion +
                  '; sudo '+linuxFlag+' make install -j8)')

    # RPP
    if os.path.exists(deps_dir+'/rpp/build-'+backend):
        os.system('sudo -v')
        os.system('(cd '+deps_dir+'/rpp/build-'+backend+'; sudo ' +
                  linuxFlag+' make install -j8)')

    # FFMPEG
    if os.path.exists(deps_dir+'/FFmpeg-n4.4.2'):
        os.system('sudo -v')
        os.system('(cd '+deps_dir+'/FFmpeg-n4.4.2; sudo ' +
                  linuxFlag+' make install -j8)')

    print("\nrocAL Dependencies Re-Installed with rocAL-setup.py V-"+__version__+"\n")
    exit()
# Clean Install
else:
    print("\nrocAL Dependencies Installation with rocAL-setup.py V-"+__version__+"\n")
    os.system('mkdir '+deps_dir)
    # Create Build folder
    os.system('(cd '+deps_dir+'; mkdir build )')
    # install pre-reqs
    os.system('sudo -v')
    os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' ' +
              linuxSystemInstall_check+' install gcc cmake git wget unzip pkg-config inxi mivisionx')

    # Get Installation Source
    os.system(
        '(cd '+deps_dir+'; wget https://github.com/opencv/opencv/archive/'+opencvVersion+'.zip )')
    os.system('(cd '+deps_dir+'; unzip '+opencvVersion+'.zip )')
    os.system(
        '(cd '+deps_dir+'; wget https://github.com/protocolbuffers/protobuf/archive/v'+ProtoBufVersion+'.zip )')
    os.system('(cd '+deps_dir+'; unzip v'+ProtoBufVersion+'.zip )')
    os.system(
        '(cd '+deps_dir+'; wget https://github.com/FFmpeg/FFmpeg/archive/refs/tags/n4.4.2.zip && unzip n4.4.2.zip )')

    # Install
    # package dependencies
    os.system('sudo -v')
    if "centos" in platfromInfo or "redhat" in platfromInfo:
        if "centos-7" in platfromInfo or "redhat-7" in platfromInfo:
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' ' + linuxSystemInstall_check +
                      ' install kernel-devel libsqlite3x-devel bzip2-devel openssl-devel python3-devel autoconf automake libtool curl make g++ unzip')
        elif "centos-8" in platfromInfo or "redhat-8" in platfromInfo:
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' ' + linuxSystemInstall_check +
                      ' install kernel-devel libsqlite3x-devel bzip2-devel openssl-devel python3-devel autoconf automake libtool curl make gcc-c++ unzip')
    elif "Ubuntu" in platfromInfo:
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' ' +
                  linuxSystemInstall_check+' install sqlite3 libsqlite3-dev libbz2-dev libssl-dev python3-dev autoconf automake libtool')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' ' +
                  linuxSystemInstall_check+' install curl make g++ unzip libomp-dev libpthread-stubs0-dev')
    elif "SLES" in platfromInfo:
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' ' +
                  linuxSystemInstall_check+' install sqlite3 sqlite3-devel libbz2-devel libopenssl-devel python3-devel autoconf automake libtool curl make gcc-c++ unzip')
    # Boost V 1.80.0 from source
    os.system(
        '(cd '+deps_dir+'; wget https://boostorg.jfrog.io/artifactory/main/release/1.80.0/source/boost_1_80_0.tar.bz2 )')
    os.system('(cd '+deps_dir+'; tar xjvf boost_1_80_0.tar.bz2 )')
    if "centos-8" in platfromInfo or "redhat-8" in platfromInfo or "SLES" in platfromInfo:
        os.system(
            '(cd '+deps_dir+'/boost_1_80_0/; ./bootstrap.sh --prefix=/usr/local --with-python=python36 )')
    else:
        os.system(
            '(cd '+deps_dir+'/boost_1_80_0/; ./bootstrap.sh --prefix=/usr/local --with-python=python3 )')
    os.system(
        '(cd '+deps_dir+'/boost_1_80_0/; ./b2 stage -j16 threading=multi link=shared cxxflags="-std=c++11" )')
    os.system(
        '(cd '+deps_dir+'/boost_1_80_0/; sudo ./b2 install threading=multi link=shared --with-system --with-filesystem)')
    os.system(
        '(cd '+deps_dir+'/boost_1_80_0/; ./b2 stage -j16 threading=multi link=static cxxflags="-std=c++11 -fpic" cflags="-fpic" )')
    os.system(
        '(cd '+deps_dir+'/boost_1_80_0/; sudo ./b2 install threading=multi link=static --with-system --with-filesystem)')
    # Install half.hpp
    os.system(
        '(cd '+deps_dir+'; wget https://sourceforge.net/projects/half/files/half/1.12.0/half-1.12.0.zip )')
    os.system('(cd '+deps_dir+'; unzip half-1.12.0.zip -d half-files )')
    os.system('sudo -v')
    os.system(
        '(cd '+deps_dir+'; sudo mkdir -p /usr/local/include/half; sudo cp half-files/include/half.hpp /usr/local/include/half )')
    # Install ProtoBuf
    os.system('(cd '+deps_dir+'/protobuf-' +
              ProtoBufVersion+'; ./autogen.sh )')
    os.system('(cd '+deps_dir+'/protobuf-' +
              ProtoBufVersion+'; ./configure )')
    os.system('(cd '+deps_dir+'/protobuf-'+ProtoBufVersion+'; make -j8 )')
    os.system('(cd '+deps_dir+'/protobuf-' +
              ProtoBufVersion+'; make check -j8 )')
    os.system('sudo -v')
    os.system('(cd '+deps_dir+'/protobuf-'+ProtoBufVersion +
              '; sudo '+linuxFlag+' make install )')
    os.system('sudo -v')
    os.system('(cd '+deps_dir+'/protobuf-'+ProtoBufVersion +
              '; sudo '+linuxFlag+' ldconfig )')

    # Install OpenCV
    os.system('(cd '+deps_dir+'/build; mkdir OpenCV )')
    # Install pre-reqs
    os.system('sudo -v')
    if "Ubuntu" in platfromInfo:
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install build-essential libgtk2.0-dev libavcodec-dev libavformat-dev libswscale-dev python-dev python-numpy ')
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev unzip')
    elif "centos" in platfromInfo or "redhat" in platfromInfo:
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' groupinstall \'Development Tools\'')
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install gtk2-devel libjpeg-devel libpng-devel libtiff-devel libavc1394 wget unzip')
    elif "SLES" in platfromInfo:
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install -t pattern devel_basis')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install gtk2-devel libjpeg-devel libpng-devel libtiff-devel libavc1394 wget unzip')
    # OpenCV 4.6.0
    os.system('(cd '+deps_dir+'/build/OpenCV; '+linuxCMake +
              ' -D WITH_GTK=ON -D WITH_JPEG=ON -D BUILD_JPEG=ON -D WITH_OPENCL=OFF -D WITH_OPENCLAMDFFT=OFF -D WITH_OPENCLAMDBLAS=OFF -D WITH_VA_INTEL=OFF -D WITH_OPENCL_SVM=OFF  -D CMAKE_INSTALL_PREFIX=/usr/local ../../opencv-'+opencvVersion+' )')
    os.system('(cd '+deps_dir+'/build/OpenCV; make -j8 )')
    os.system('sudo -v')
    os.system('(cd '+deps_dir+'/build/OpenCV; sudo '+linuxFlag+' make install )')
    os.system('sudo -v')
    os.system('(cd '+deps_dir+'/build/OpenCV; sudo '+linuxFlag+' ldconfig )')

    # Install RPP
    if "Ubuntu" in platfromInfo:
        # Install Packages for rocAL
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' ' +
                  linuxSystemInstall_check+' install libgflags-dev libgoogle-glog-dev liblmdb-dev')
        # Yasm/Nasm for TurboJPEG
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall +
                  ' '+linuxSystemInstall_check+' install nasm yasm')
        # clang
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' ' +
                  linuxSystemInstall_check+' install clang')
        # turbo-JPEG - https://github.com/rrawther/libjpeg-turbo.git -- 2.0.6.2
        os.system(
            '(cd '+deps_dir+'; git clone -b 2.0.6.2 https://github.com/rrawther/libjpeg-turbo.git )')
        os.system('(cd '+deps_dir+'/libjpeg-turbo; mkdir build; cd build; '+linuxCMake +
                  ' -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=RELEASE -DENABLE_STATIC=FALSE -DCMAKE_INSTALL_DEFAULT_LIBDIR=lib ..; make -j 4; sudo make install )')
        # RPP
        os.system('sudo -v')
        os.system('(cd '+deps_dir+'; git clone -b '+rppVersion+' https://github.com/GPUOpen-ProfessionalCompute-Libraries/rpp.git; cd rpp; mkdir build-'+backend+'; cd build-'+backend+'; ' +
                  linuxCMake+' -DBACKEND='+backend+' ../; make -j4; sudo make install)')
        # Turn off for CentOS - TBD: TURN ON when RPP is supported on CentOS
        # else:
        # Nasm
        # os.system('(cd '+deps_dir+'; curl -O -L https://www.nasm.us/pub/nasm/releasebuilds/2.14.02/nasm-2.14.02.tar.bz2 )')
        # os.system('(cd '+deps_dir+'; tar xjvf nasm-2.14.02.tar.bz2 )')
        # os.system('(cd '+deps_dir+'/nasm-2.14.02; ./autogen.sh; ./configure; make -j8 )')
        # os.system('sudo -v')
        # os.system('(cd '+deps_dir+'/nasm-2.14.02; sudo '+linuxFlag+' make install )')
        # Yasm
        # os.system('(cd '+deps_dir+'; curl -O -L https://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz )')
        # os.system('(cd '+deps_dir+'; tar xzvf yasm-1.3.0.tar.gz )')
        # os.system('(cd '+deps_dir+'/yasm-1.3.0; ./configure; make -j8 )')
        # os.system('sudo -v')
        # os.system('(cd '+deps_dir+'/yasm-1.3.0; sudo '+linuxFlag+' make install )')
        # JSON-cpp
        # os.system('sudo -v')
        # os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check+' install jsoncpp')
        # clang+boost
        # os.system('sudo -v')
        # os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check+' install boost-devel clang')
        # turbo-JPEG
        # os.system('(cd '+deps_dir+'; wget https://downloads.sourceforge.net/libjpeg-turbo/libjpeg-turbo-2.0.3.tar.gz )')
        # os.system('(cd '+deps_dir+'; tar xf libjpeg-turbo-2.0.3.tar.gz )')
        # os.system('(cd '+deps_dir+'/libjpeg-turbo-2.0.3; mkdir build; cd build; '+linuxCMake+' -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=RELEASE -DENABLE_STATIC=FALSE -DCMAKE_INSTALL_DOCDIR=/usr/share/doc/libjpeg-turbo-2.0.3 -DCMAKE_INSTALL_DEFAULT_LIBDIR=lib ..; make -j 4; sudo make install )')
        # RPP
        # os.system('(cd '+deps_dir+'; git clone -b '+rppVersion+' https://github.com/GPUOpen-ProfessionalCompute-Libraries/rpp.git; cd rpp; mkdir build; cd build; '+linuxCMake+' -DBACKEND=OCL ../; make -j4; sudo make install)')

    # Install ffmpeg
    if "Ubuntu" in platfromInfo:
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install autoconf automake build-essential git-core libass-dev libfreetype6-dev')
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install libsdl2-dev libtool libva-dev libvdpau-dev libvorbis-dev libxcb1-dev')
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install libxcb-shm0-dev libxcb-xfixes0-dev pkg-config texinfo zlib1g-dev')
        os.system('sudo -v')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install nasm yasm libx264-dev libx265-dev libnuma-dev libfdk-aac-dev')
    else:
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install autoconf automake bzip2 bzip2-devel freetype-devel')
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install gcc-c++ libtool make pkgconfig zlib-devel')
        # Nasm
        os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                  ' install nasm')
        if "centos-7" in platfromInfo or "redhat-7" in platfromInfo:
            # Yasm
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' install http://repo.okay.com.mx/centos/7/x86_64/release/okay-release-1-1.noarch.rpm')
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' --enablerepo=extras install epel-release')
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' install yasm')
            # libx264 & libx265
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' install libx264-devel libx265-devel')
            # libfdk_aac
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' install https://forensics.cert.org/cert-forensics-tools-release-el7.rpm')
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' --enablerepo=forensics install fdk-aac')
            # libASS
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' install libass-devel')
        elif "centos-8" in platfromInfo or "redhat-8" in platfromInfo:
            # el8 x86_64 packages
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm')
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' install https://download1.rpmfusion.org/free/el/rpmfusion-free-release-8.noarch.rpm https://download1.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-8.noarch.rpm')
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' install http://mirror.centos.org/centos/8/PowerTools/x86_64/os/Packages/SDL2-2.0.10-2.el8.x86_64.rpm')
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' install ffmpeg ffmpeg-devel')
        elif "SLES" in platfromInfo:
            # FFMPEG-4 packages
            os.system(
                'sudo zypper ar -cfp 90 \'https://ftp.gwdg.de/pub/linux/misc/packman/suse/openSUSE_Leap_$releasever/Essentials\' packman-essentials')
            os.system('sudo '+linuxFlag+' '+linuxSystemInstall+' '+linuxSystemInstall_check +
                      ' install ffmpeg-4')

        # FFMPEG 4 from source -- for Ubuntu, CentOS 7, & RedHat 7
        if "Ubuntu" in platfromInfo or "centos-7" in platfromInfo or "redhat-7" in platfromInfo:
            os.system('sudo -v')
            os.system(
                '(cd '+deps_dir+'/FFmpeg-n4.4.2; sudo '+linuxFlag+' ldconfig )')
            os.system('(cd '+deps_dir+'/FFmpeg-n4.4.2; export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig/"; ./configure --enable-shared --disable-static --enable-libx264 --enable-libx265 --enable-libfdk-aac --enable-libass --enable-gpl --enable-nonfree)')
            os.system('(cd '+deps_dir+'/FFmpeg-n4.4.2; make -j8 )')
            os.system('sudo -v')
            os.system('(cd '+deps_dir+'/FFmpeg-n4.4.2; sudo ' +
                      linuxFlag+' make install )')

    # MIVisionX
    os.system('sudo -v')
    os.system('(cd '+deps_dir+'; git clone -b '+mivisionxVersion+' https://github.com/GPUOpen-ProfessionalCompute-Libraries/MIVisionX.git; cd MIVisionX; mkdir build-'+backend+'; cd build-'+backend+'; ' +
                  linuxCMake+' -DBACKEND='+backend+' ../; make -j4; sudo make install)')

    print("\nrocAL Dependencies Installed with rocAL-setup.py V-"+__version__+"\n")
