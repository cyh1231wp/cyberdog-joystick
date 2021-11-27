sudo pip install grpcio
sudo pip install grpcio-tools
sudo cp joystick.service /lib/systemd/system
sudo systemctl daemon-reload
sudo systemctl start joystick
sudo systemctl enable joystick