# Cyberdog-Joystick
本项目可以实现铁蛋开机后自动搜索蓝牙手柄，并通过蓝牙手柄控制铁蛋的运动方向以及几个常用动作。

####蓝牙配对
通过nomachine或者hdmi线进入铁蛋的桌面后，打开蓝牙界面（Devices），选择自己的蓝牙手柄信号（我的为T-3）进行pair，并trust。至此，蓝牙手柄在下次开机时就可以自动连接铁蛋。

####安装脚本
```
cd /home/mi/Desktop
git clone https://github.com/cyh1231wp/cyberdog-joystick.git
chmod -R 777 cyberdog-joystick
cd cyberdog-joystick
sudo bash install.sh
```
执行完上述代码之后，拔掉充电线，按start按钮启动铁蛋，等待遥控器自动连接上即可控制。（插电状态无法让铁蛋运动）
