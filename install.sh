pip install grpcio
pip install grpcio-tools

cp joystick /etc/init.d/
chmod +x /etc/init.d/joystick
ln -sf /etc/init.d/joystick /usr/bin/joystick

systemctl enable joystick