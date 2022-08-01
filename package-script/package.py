#!/usr/bin/env python3
# 使用系统默认的 python3 运行
###########################################################################################
# 作者：gfdgd xi、为什么您不喜欢熊出没和阿布呢
# 版本：1.7.1
# 更新时间：2022年07月19日
# 感谢：感谢 wine 以及 deepin-wine 团队，提供了 wine 和 deepin-wine 给大家使用，让我能做这个程序
# 基于 Python3 的 tkinter 构建
###########################################################################################
#################
# 引入所需的库
#################
import os
import sys
import json
import subprocess
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

###################
# 程序所需事件
###################
# 读取文本文档
def readtxt(path):
    f = open(path, "r") # 设置文件对象
    str = f.read()  # 获取内容
    f.close()  # 关闭文本对象
    return str  # 返回结果

# 获取用户主目录
def get_home():
    return os.path.expanduser('~')

# 写入文本文档
def WriteTXT(path, things):
    file = open(path, 'w', encoding='UTF-8')  # 设置文件对象
    file.write(things)  # 写入文本
    file.close()  # 关闭文本对象

def DisbledOrEnabled(choose: bool):
    chineseName.setDisabled(choose)
    englishName.setDisabled(choose), 
    debDescription.setDisabled(choose)
    typeName.setDisabled(choose)
    exePath.setDisabled(choose) 
    packageName.setDisabled(choose)
    versionName.setDisabled(choose)
    buildDeb.setDisabled(choose)


class PackageDebThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(str)
    def __init__(self) -> None:
        super().__init__()

    def run(self):
        startupWMClassName = os.path.basename(exePath.text().replace("\\", "/"))
        print(startupWMClassName)
        WriteTXT(f"{programPath}/package-hshw.sh", f"""#!/bin/bash

#最终生成的包的描述
export app_description="{debDescription.text()}"
#应用程序英文名
export app_name="{englishName.text()}"
#应用程序中文名
export app_name_zh_cn="{chineseName.text()}"
#desktop文件中的分类
export desktop_file_categories="{typeName.currentText()};"
#desktop文件中StartupWMClass字段。用于让桌面组件将窗口类名与desktop文件相对应。这个值为实际运行的主程序EXE的文件名，wine/crossover在程序运行后会将文件名设置为窗口类名
export desktop_file_main_exe="{startupWMClassName}"
export exec_path="{exePath.text()}"
#最终生成的包的包名,包名的命名规则以deepin开头，加官网域名（需要前后对调位置），如还不能区分再加上应用名
export deb_package_name="{packageName.text()}"
#最终生成的包的版本号，版本号命名规则：应用版本号+deepin+数字
export deb_version_string="{versionName.text()}"

export package_depends="deepin-wine6-stable:amd64 (>= 6.0.0.12-1), deepin-wine-helper (>= 5.1.25-1)"
export apprun_cmd="deepin-wine6-stable"
#export package_depends="deepin-wine5-stable:amd64 (>= 5.0.29-1), deepin-wine-helper (>= 5.1.25-1)"
#export apprun_cmd="deepin-wine5-stable"

# rm -fr final.dir/
# rm -fr icons/
# rm -fr staging.dir/

./script-packager.sh $@
""")
        os.chdir(programPath)
        res = subprocess.Popen(["./package-hshw.sh"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # 实时读取程序返回
        while res.poll() is None:
            try:
                text = res.stdout.readline().decode("utf8")
            except:
                text = ""
            self.signal.emit(text)
            print(text, end="")
        
        DisbledOrEnabled(False)

class QT:
    run = None

def PackageDeb():
    DisbledOrEnabled(True)
    for i in [chineseName.text(), englishName.text(), debDescription.text(), typeName.currentText(), exePath.text(), packageName.text(), versionName.text()]:
        if i == "":
            QtWidgets.QMessageBox.information(widget, "提示", "您未填完所有信息，无法继续")
            DisbledOrEnabled(False)
            return
    commandReturn.setText("")
    QT.run = PackageDebThread()
    QT.run.signal.connect(RunCommand)
    QT.run.start()

def RunCommand(command):
    commandReturn.append(command)

def ShowHelp():
    QtWidgets.QMessageBox.information(widget, "帮助", f"下面是有关打包器的各个输入框的意义以及有关的 UOS 填写标准\n{tips}")

def OpenPackageFolder():
    os.system(f"xdg-open '{programPath}/package_save/uos'")

###########################
# 程序信息
###########################
programPath = os.path.split(os.path.realpath(__file__))[0]  # 返回 string
information = json.loads(readtxt(f"{programPath}/information.json"))
version = information["Version"]
iconPath = "{}/deepin-wine-runner.svg".format(programPath)
tips = """第一个文本框是应用程序中文名
第二个文本框是应用程序英文名
第三个文本框是最终生成的包的描述
第四个选择框是desktop文件中的分类
第五个输入框是程序在 Wine 容器的位置，以 c:\\XXX 的形式，盘符必须小写，用反斜杠，如果路径带用户名的话会自动替换为$USER
而 StartupWMClass 字段将会由程序自动生成，作用如下：
desktop文件中StartupWMClass字段。用于让桌面组件将窗口类名与desktop文件相对应。这个值为实际运行的主程序EXE的文件名，wine/crossover在程序运行后会将文件名设置为窗口类名
第六个输入框是最终生成的包的包名,包名的命名规则以deepin开头，加官网域名（需要前后对调位置），如还不能区分再加上应用名
最后一个是最终生成的包的版本号，版本号命名规则：应用版本号+deepin+数字
"""

###########################
# 窗口创建
###########################
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
widget = QtWidgets.QWidget()
widgetLayout = QtWidgets.QGridLayout()

size = QtWidgets.QSizePolicy()
size.setHorizontalPolicy(0)

chineseName = QtWidgets.QLineEdit()
englishName = QtWidgets.QLineEdit()
debDescription = QtWidgets.QLineEdit()
typeName = QtWidgets.QComboBox()
exePath = QtWidgets.QLineEdit()
packageName = QtWidgets.QLineEdit()
versionName = QtWidgets.QLineEdit()
controlFrame = QtWidgets.QHBoxLayout()
buildDeb = QtWidgets.QPushButton("打包")
debPath = QtWidgets.QPushButton("deb 包生成目录")
buildDeb.setSizePolicy(size)
debPath.setSizePolicy(size)
commandReturn = QtWidgets.QTextBrowser()
typeName.addItems(["Network", "Chat", "Audio", "Video", "Graphics", "Office", "Translation", "Development", "Utility", "System"])
controlFrame.addWidget(buildDeb)
controlFrame.addWidget(debPath)
widgetLayout.addWidget(QtWidgets.QLabel("程序中文名："), 0, 0, 1, 1)
widgetLayout.addWidget(QtWidgets.QLabel("程序英文名："), 1, 0, 1, 1)
widgetLayout.addWidget(QtWidgets.QLabel("包描述："), 2, 0, 1, 1)
widgetLayout.addWidget(QtWidgets.QLabel("程序分类："), 3, 0, 1, 1)
widgetLayout.addWidget(QtWidgets.QLabel("程序在 Wine 容器的位置："), 4, 0, 1, 1)
widgetLayout.addWidget(QtWidgets.QLabel("包名："), 5, 0, 1, 1)
widgetLayout.addWidget(QtWidgets.QLabel("版本号："), 6, 0, 1, 1)
widgetLayout.addWidget(chineseName, 0, 1, 1, 1)
widgetLayout.addWidget(englishName, 1, 1, 1, 1)
widgetLayout.addWidget(debDescription, 2, 1, 1, 1)
widgetLayout.addWidget(typeName, 3, 1, 1, 1)
widgetLayout.addWidget(exePath, 4, 1, 1, 1)
widgetLayout.addWidget(packageName, 5, 1, 1, 1)
widgetLayout.addWidget(versionName, 6, 1, 1, 1)
widgetLayout.addLayout(controlFrame, 7, 0, 1, 2)
widgetLayout.addWidget(commandReturn, 8, 0, 1, 2)
buildDeb.clicked.connect(PackageDeb)
debPath.clicked.connect(OpenPackageFolder)
widget.setLayout(widgetLayout)
window.setCentralWidget(widget)
window.resize(window.frameGeometry().width() * 1.5, window.frameGeometry().height())
window.setWindowIcon(QtGui.QIcon(iconPath))
menu = window.menuBar()
programMenu = menu.addMenu("程序")
exit = QtWidgets.QAction("退出")
exit.triggered.connect(window.close)
helpMenu = menu.addMenu("帮助")
help = QtWidgets.QAction("帮助")
help.triggered.connect(ShowHelp)
helpMenu.addAction(help)
programMenu.addAction(exit)
print(iconPath)
window.show()
window.setWindowTitle(f"Wine 打包器 {version}——基于统信 Wine 生态活动打包脚本制作")
windowFrameInputValueList = [
    chineseName,
    englishName,
    debDescription,
    typeName,
    exePath,
    packageName,
    versionName
]
sys.exit(app.exec_())