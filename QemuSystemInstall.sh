#!/bin/bash
sudo apt update
sudo apt install qemu-system qemu-user qemu-efi qemu-efi-aarch64 -y
sudo apt install qemu-user-static binfmt-support qemu-system-gui -y
echo 安装完成！按回车键退出
read
