install build-essential cmake pkg-config unzip yasm git checkinstall libjpeg-dev libpng-dev libtiff-dev 
install libavcodec-dev libavformat-dev libswscale-dev libavresample-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libxvidcore-dev x264 libx264-dev libfaac-dev libmp3lame-dev libtheora-dev libfaac-dev libmp3lame-dev libvorbis-dev
install libopencore-amrnb-dev libopencore-amrwb-dev
install libdc1394-22 libdc1394-22-dev libxine2-dev libv4l-dev v4l-utils
cwd=$(pwd)
cd /usr/include/linux
sudo ln -s -f ../libv4l1-videodev.h videodev.h
cd "$cwd"
install libgtk-3-dev
install python3-dev python3-pip
sudo -H pip3 install -U pip numpy
install python3-testresources
install libatlas-base-dev gfortran
#install libprotobuf-dev protobuf-compiler libgoogle-glog-dev libgflags-dev libgphoto2-dev libeigen3-dev libhdf5-dev doxygen
cd ~/Downloads
wget -O opencv.zip https://github.com/opencv/opencv/archive/refs/tags/4.5.2.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/refs/tags/4.5.2.zip
unzip opencv.zip
unzip opencv_contrib.zip
#echo "Create a virtual environtment for the python binding module (OPTIONAL)"
#sudo pip install virtualenv virtualenvwrapper
#sudo rm -rf ~/.cache/pip
#echo "Edit ~/.bashrc"
#export WORKON_HOME=$HOME/.virtualenvs
#export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
#source /usr/local/bin/virtualenvwrapper.sh
#mkvirtualenv cv -p python3
cd opencv-4.5.2
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE CMAKE_INSTALL_PREFIX=/usr/local WITH_TBB=ON ENABLE_FAST_MATH=1 CUDA_FAST_MATH=1 WITH_CUBLAS=1 WITH_CUDA=ON BUILD_opencv_cudacodec=ON WITH_CUDNN=ON OPENCV_DNN_CUDA=ON CUDA_ARCH_BIN=6.1 WITH_V4L=ON WITH_QT=ON WITH_OPENGL=ON WITH_GSTREAMER=ON OPENCV_GENERATE_PKGCONFIG=ON OPENCV_PC_FILE_NAME=opencv.pc OPENCV_ENABLE_NONFREE=ON OPENCV_PYTHON3_INSTALL_PATH=/usr/local/lib/python3.8/dist-packages PYTHON_EXECUTABLE=/usr/bin/python3 OPENCV_EXTRA_MODULES_PATH=~/Downloads/opencv_contrib-4.5.2/modules INSTALL_PYTHON_EXAMPLES=ON INSTALL_C_EXAMPLES=ON BUILD_EXAMPLES=OFF ..
n=$(nproc)
make -j$n
read -p "ready to install! Press enter..."
sudo make install

