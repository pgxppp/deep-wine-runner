#!/bin/sh
# 使用系统默认的 sh 运行
#################################################################################################################
# 作者：gfdgd xi
# 版本：3.0.0
# 更新时间：2022年10月02日
# 感谢：感谢 wine、deepin-wine 以及星火团队，提供了 wine、deepin-wine、spark-wine-devel 给大家使用，让我能做这个程序
# 基于 sh
#################################################################################################################
# 非强制性的必应组件，所以成功不成功都行
# 程序版本号
version=3.4.0
echo 安装组件
python3 -m pip install --upgrade pynput --trusted-host https://repo.huaweicloud.com -i https://repo.huaweicloud.com/repository/pypi/simple --break-system-packages > /dev/null 2>&1 | true
python3 -m pip install --upgrade xpinyin --trusted-host https://repo.huaweicloud.com -i https://repo.huaweicloud.com/repository/pypi/simple --break-system-packages > /dev/null 2>&1 | true
echo 执行完成
echo 移除旧组件
if [ -d /opt/apps/deepin-wine-runner/arm-package ]; then
	rm -rf /opt/apps/deepin-wine-runner/arm-package
fi
if [ -d /opt/apps/deepin-wine-runner/dlls-arm ]; then
	rm -rf /opt/apps/deepin-wine-runner/dlls-arm
fi
if [ -d /opt/apps/deepin-wine-runner/exa ]; then
	rm -rf /opt/apps/deepin-wine-runner/exa
fi
if [ -d /opt/apps/deepin-wine-runner/dxvk ]; then
	rm -rf /opt/apps/deepin-wine-runner/dxvk
fi
echo 移除完成
# 如果为非 X86 PC，可以删除掉一些无用组件（主要是用不了）
if [ `arch` != "x86_64" ]; then
	echo 非X86架构，删除对非X86架构无用的组件
	# 删除虚拟机功能
	#rm -rf /opt/apps/deepin-wine-runner/StartVM.sh
	#rm -rf /opt/apps/deepin-wine-runner/RunVM.sh
	#rm -rf /opt/apps/deepin-wine-runner/VM
	#rm -rf /usr/share/applications/spark-deepin-wine-runner-control-vm.desktop
	#rm -rf /usr/share/applications/spark-deepin-wine-runner-start-vm.desktop
	# 删除安装 wine 功能
	rm -rf "/opt/apps/deepin-wine-runner/wine install"
	# 这个注释掉的理论可用，不移除
	#rm -rf "/opt/apps/deepin-wine-runner/wine"
	rm -rf /usr/bin/deepin-wine-runner-wine-installer
	rm -rf /usr/bin/deepin-wine-runner-wine-install-deepin23
	rm -rf /usr/bin/deepin-wine-runner-wine-install
	rm -rf /usr/bin/deepin-wine-runner-winehq-install
	rm -rf /opt/apps/deepin-wine-runner/InstallWineOnDeepin23.py
	rm -rf /opt/apps/deepin-wine-runner/sparkstore.list
	rm -rf /opt/apps/deepin-wine-runner/AllInstall.py
	rm -rf /opt/apps/deepin-wine-runner/InstallNewWineHQ.sh
fi
# 处理 VM 工具
vmPath=/opt/apps/deepin-wine-runner/VM/VirtualMachine-`dpkg --print-architecture`
echo 当前架构为：`dpkg --print-architecture`
if [ -f $vmPath ]; then
	echo 虚拟机工具有该架构的预编译文件
	# 移除辅助文件
	rm -f /opt/apps/deepin-wine-runner/VM/VirtualMachine
	# 移动
	mv $vmPath /opt/apps/deepin-wine-runner/VM/VirtualMachine
	rm -f /opt/apps/deepin-wine-runner/VM/VirtualMachine-*
else
	echo 虚拟机工具无该架构的预编译文件
	rm -f /opt/apps/deepin-wine-runner/VM/VirtualMachine-*
fi
echo 处理完成！
# 修复 3.3.0.1 Box86 源挂了的问题
if [ -f /etc/apt/sources.list.d/box86.list ]; then
	bash -c "echo deb http://seafile.jyx2048.com:2345/spark-deepin-wine-runner/data/box86-debs/debian ./ > /etc/apt/sources.list.d/box86.list"
fi
# Gitlink 源挂了
# 到时候切换 gpg 源会方便很多
#if [ -r /etc/apt/sources.list.d/better-dde.list ]; then
#	if [ -d /usr/share/deepin-installer ]; then
#		# 用于修复 Deepin Community Live CD Install 版签名过期的问题
#		wget -P /tmp/gfdgd-xi-sources https://code.gitlink.org.cn/gfdgd_xi/gfdgd-xi-apt-mirrors/raw/branch/master/gpg.asc
#		rm -rfv /etc/apt/trusted.gpg.d/gfdgdxi-list.gpg | true
#		cp -v /tmp/gfdgd-xi-sources/gpg.asc.gpg /etc/apt/trusted.gpg.d/gfdgdxi-list.gpg
#   	# 用于修复 2022.11.25 Better DDE 导致的 Deepin Community Live CD Install 版问题
#		# 移除 Better DDE 源
#    	rm -rfv /etc/apt/sources.list.d/better-dde.list
#		apt update > /dev/null 2>&1 | true
#	fi
#fi
# 设置目录权限，让用户可读可写，方便后续删除组件
chmod 777 -R /opt/apps/deepin-wine-runner
# 向服务器返回安装数加1（不显示内容且忽略错误）
python3 /opt/apps/deepin-wine-runner/Download.py $version > /dev/null 2>&1 | true
