import os
import sys
import json
import requests
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(693, 404)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.localWineList = QtWidgets.QListView(self.centralWidget)
        self.localWineList.setObjectName("localWineList")
        self.horizontalLayout_2.addWidget(self.localWineList)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.addButton = QtWidgets.QPushButton(self.centralWidget)
        self.addButton.setObjectName("addButton")
        self.verticalLayout.addWidget(self.addButton)
        self.delButton = QtWidgets.QPushButton(self.centralWidget)
        self.delButton.setObjectName("delButton")
        self.verticalLayout.addWidget(self.delButton)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.internetWineList = QtWidgets.QListView(self.centralWidget)
        self.internetWineList.setObjectName("internetWineList")
        self.horizontalLayout_2.addWidget(self.internetWineList)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.unzip = QtWidgets.QCheckBox(self.centralWidget)
        self.unzip.setObjectName("unzip")
        self.horizontalLayout.addWidget(self.unzip)
        self.deleteZip = QtWidgets.QCheckBox(self.centralWidget)
        self.deleteZip.setChecked(True)
        self.deleteZip.setTristate(False)
        self.deleteZip.setObjectName("deleteZip")
        self.horizontalLayout.addWidget(self.deleteZip)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "下载 Wine"))
        self.addButton.setText(_translate("MainWindow", "<<"))
        self.delButton.setText(_translate("MainWindow", ">>"))
        self.unzip.setText(_translate("MainWindow", "不解压Wine资源文件"))
        self.deleteZip.setText(_translate("MainWindow", "删除下载的资源包，只解压保留（两个选项都选相互抵消）"))

def ReadLocalInformation():
    global localJsonList
    file = open(f"{programPath}/winelist.json", "r")
    localJsonList = json.loads(file.read())
    nmodel = QtGui.QStandardItemModel(window)
    for i in localJsonList:
        item = QtGui.QStandardItem(i)
        nmodel.appendRow(item)
    ui.localWineList.setModel(nmodel)
    file.close()

def ReadInternetInformation():
    global internetJsonList
    # C++ 版本是用 curl 的，考虑到 Python 用 requests 反而方便，于是不用 curl
    internetJsonList = json.loads(requests.get(f"{internetWineSource}/information.json").text)
    nmodel = QtGui.QStandardItemModel(window)
    for i in internetJsonList:
        item = QtGui.QStandardItem(i[0])
        nmodel.appendRow(item)
    ui.internetWineList.setModel(nmodel)
    
class DownloadThread(QtCore.QThread):
    MessageBoxInfo = QtCore.pyqtSignal(str)
    MessageBoxError = QtCore.pyqtSignal(str)
    ChangeDialog = QtCore.pyqtSignal(QtWidgets.QProgressDialog, int, int, int)
    Finish = QtCore.pyqtSignal()
    def __init__(self, progressDialog: QtWidgets.QProgressDialog, 
        url: str, savePath: str, fileName: str, view: QtWidgets.QListView, deleteZip: bool, 
        unzip: bool, localList) -> None:
        self.dialog = progressDialog
        self.fileUrl = url
        self.fileSavePath = savePath
        self.fileSaveName = fileName
        self.localView = view
        self.downloadDeleteZip = deleteZip
        self.downloadUnzip = unzip
        self.localJsonList = localList
        super().__init__()

    def ReadLocalInformation(self):
        file = open(f"{programPath}/winelist.json", "r");
        nmodel = QtGui.QStandardItemModel()
        localJsonList = json.loads(file.read())
        for i in localJsonList:
            nmodel.appendRow(QtGui.QStandardItem(i))
        self.localView.setModel(nmodel)
        file.close()

    def run(self):
        # 创建文件夹
        dir = QtCore.QDir()
        savePath = f"{programPath}/{self.fileSaveName}"
        # 文件下载
        timeout = 0
        f = requests.get(self.fileUrl, stream=True)
        allSize = int(f.headers["content-length"])  # 文件总大小
        bytesRead = 0
        with open(savePath, "wb") as filePart:
            for chunk in f.iter_content(chunk_size=1024):
                if chunk:
                    #progressbar.update(int(part / show))
                    filePart.write(chunk)
                    bytesRead += 1024
                    self.ChangeDialog.emit(self.dialog, bytesRead / allSize * 100, bytesRead / 1024 / 1024, allSize / 1024 / 1024)
        # 写入配置文件
        rfile = open(f"{programPath}/winelist.json", "r")
        list = json.loads(rfile.read())
        rfile.close()
        # C++ 版注释：不直接用 readwrite 是因为不能覆盖写入
        file = open(f"{programPath}/winelist.json", "w")
        list.append(self.fileSaveName.replace(".7z", ""))
        file.write(json.dumps(list))
        file.close()
        # 读取配置文件
        self.ReadLocalInformation()
        self.localJsonList = list
        # 解压文件
        shellCommand = ""
        if self.downloadUnzip:
            path = f"{programPath}/{self.fileSaveName.replace('.7z', '')}"
            shellCommand += f"""mkdir -p \"{path}\"
7z x \"{savePath}\" -o\"{path}\"
"""
        if self.downloadDeleteZip:
            shellCommand += f"rm -rf \"{savePath}\"\n"
        shellFile = open("/tmp/depein-wine-runner-wine-install.sh", "w")
        shellFile.write(shellCommand)
        shellFile.close()
        process = QtCore.QProcess()
        command = ["deepin-terminal", "-e", "bash", "/tmp/depein-wine-runner-wine-install.sh"]
        process.start(f"{programPath}/../launch.sh", command)
        process.waitForFinished()
        self.Finish.emit()


def MessageBoxInfo(info):
    QtWidgets.QMessageBox.information(window, "提示", info)

def MessageBoxError(info):
    QtWidgets.QMessageBox.critical(window, "错误", info)

def ChangeDialog(dialog: QtWidgets.QProgressDialog, value, downloadBytes, totalBytes):
    dialog.setValue(value)
    dialog.setLabelText(f"{downloadBytes}MB/{totalBytes}MB")

def DownloadFinish():
    ui.centralWidget.setEnabled(True)

class QT:
    thread = None

def on_addButton_clicked():
    choose = ui.internetWineList.currentIndex().row()
    if choose < 0:
        QtWidgets.QMessageBox.information(window, "提示", "您未选中任何项，无法继续")
        return
    downloadName = internetJsonList[choose][1]
    ReadLocalInformation()
    for i in localJsonList:
        if i == internetJsonList[choose][0]:
            QtWidgets.QMessageBox.information(window, "提示", "您已经安装了这个Wine了！无需重复安装！")
            return
    if(ui.deleteZip.isChecked() + ui.unzip.isChecked() == 2):
        ui.deleteZip.setChecked(False)
        ui.unzip.setChecked(False)
    downloadUrl = internetWineSource + downloadName
    dialog = QtWidgets.QProgressDialog()
    cancel = QtWidgets.QPushButton("取消")
    cancel.setDisabled(True)
    dialog.setWindowIcon(QtGui.QIcon(f"{programPath}/../deepin-wine-runner.svg"))
    dialog.setCancelButton(cancel)
    dialog.setWindowTitle(f"正在下载“{internetJsonList[choose][0]}”")
    QT.thread = DownloadThread(
        dialog, 
        downloadUrl, 
        "", 
        internetJsonList[choose][1],
        ui.localWineList,
        ui.deleteZip.isChecked(),
        not ui.unzip.isChecked(),
        localJsonList
        )
    QT.thread.MessageBoxInfo.connect(MessageBoxInfo)
    QT.thread.MessageBoxError.connect(MessageBoxError)
    QT.thread.ChangeDialog.connect(ChangeDialog)
    QT.thread.Finish.connect(DownloadFinish)
    ui.centralWidget.setDisabled(True)
    QT.thread.start()

def on_delButton_clicked():
    if QtWidgets.QMessageBox.question(window, "提示", "你确定要删除吗？") == QtWidgets.QMessageBox.No:
        return
    if ui.localWineList.currentIndex().row() < 0:
        QtWidgets.QMessageBox.information(window, "提示", "您未选择任何项")
        return
    name = f"{programPath}/{localJsonList[ui.localWineList.currentIndex().row()]}"
    dir = QtCore.QDir(name)
    dir.removeRecursively()
    QtCore.QFile.remove(name + ".7z")
    del localJsonList[ui.localWineList.currentIndex().row()]
    file = open(f"{programPath}/winelist.json", "w")
    file.write(json.dumps(localJsonList))
    file.close()
    ReadLocalInformation()
    QtWidgets.QMessageBox.information(window, "提示", "删除成功！")

if __name__ == "__main__":
    localJsonList = []
    internetJsonList = []
    internetWineSource = "https://code.gitlink.org.cn/gfdgd_xi/wine-mirrors/raw/branch/master/"
    programPath = os.path.split(os.path.realpath(__file__))[0]  # 返回 string
    app = QtWidgets.QApplication(sys.argv)
    # 窗口构建
    window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    # 连接信号
    ui.addButton.clicked.connect(on_addButton_clicked)
    ui.delButton.clicked.connect(on_delButton_clicked)
    ## 加载内容
    # 设置列表双击不会编辑
    ui.localWineList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    ui.internetWineList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    # 读取信息
    ReadLocalInformation()
    ReadInternetInformation()
    # 图标
    ui.centralWidget.setWindowIcon(QtGui.QIcon(f"{programPath}/../deepin-wine-runner.svg"))

    app.exec_()