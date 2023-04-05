/*
 * gfdgd xi、为什么您不喜欢熊出没和阿布呢
 * 依照 GPLV3 开源
 */
#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void ShowCPUMessage();
    void on_browser_clicked();
    QString GetRunCommand(QString command);
    void on_install_clicked();


private:
    Ui::MainWindow *ui;
    long m_cpuAll;
    long m_cpuFree;
};

#endif // MAINWINDOW_H
