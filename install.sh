#sudo pip install grpcio
#sudo pip install grpcio-tools
sudo cp joystick /etc/init.d
sudo chmod +x /etc/init.d/joystick
sudo ln -sf /etc/init.d/joystick /usr/bin/joystick
sudo update-rc.d joystick defaults
sudo /etc/init.d/joystick start