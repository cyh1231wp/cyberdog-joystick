# sudo pip install grpcio
# sudo pip install grpcio-tools
sudo cp joystick.service /lib/systemd/system
sudo systemctl daemon-reload
sudo systemctl start joystick
sudo systemctl enable joystick
# sudo cp init /etc/init.d/joystick
# sudo chmod 777 /etc/init.d/joystick
# sudo update-rc.d joystick defaults