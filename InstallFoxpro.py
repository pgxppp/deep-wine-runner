#!/usr/bin/env python3
# 使用系统默认的 python3 运行
###########################################################################################
# 作者：gfdgd xi
# 版本：2.1.0
# 更新时间：2022年08月25日
# 感谢：感谢 wine 以及 deepin-wine 团队，提供了 wine 和 deepin-wine 给大家使用，让我能做这个程序
# 基于 Python3 构建
###########################################################################################
#################
# 引入所需的库
#################
import os
import sys
import json
import updatekiller
import req as requests
try:
    sourcesList = [
        "http://foxpro.wine-runner.gfdgdxi.top/list.json",
        "https://code.gitlink.org.cn/gfdgd_xi/wine-runner-list/raw/branch/master/Visual FoxPro/list.json"
    ]
    change = False
    for i in sourcesList:
        try:
            netList = json.loads(requests.get(i).text)
            change = True
            break
        except:
            pass
    if not change:
        netList = json.loads(requests.get(sourcesList[0]).text)
except:
    print("使用离线列表")
    netList = [
        ["3.0 Runtime Service Pack 1", "http://foxpro.wine-runner.gfdgdxi.top/VFP3SP1RT.EXE", "VFP3SP1RT.EXE"],
        ["5.0 Runtime Service Pack 1", "http://foxpro.wine-runner.gfdgdxi.top/VFP5SP1RT.EXE", "VFP5SP1RT.EXE"],
        ["6.0 Runtime Service Pack 5", "http://foxpro.wine-runner.gfdgdxi.top/VFP6SP5RT.EXE", "VFP6SP5RT.EXE"],
        ["7.0 Runtime Service Pack 0", "http://foxpro.wine-runner.gfdgdxi.top/VFP7SP0RT.EXE", "VFP7SP0RT.EXE"],
        ["7.0 Runtime Service Pack 1", "http://foxpro.wine-runner.gfdgdxi.top/VFP7SP1RT.EXE", "VFP7SP1RT.EXE"],
        ["8.0 Runtime Service Pack 0", "http://foxpro.wine-runner.gfdgdxi.top/VFP8SP0RT.EXE", "VFP8SP0RT.EXE"],
        ["8.0 Runtime Service Pack 1", "http://foxpro.wine-runner.gfdgdxi.top/VFP8SP1RT.EXE", "VFP8SP1RT.EXE"],
        ["9.0 Runtime Service Pack 1", "http://foxpro.wine-runner.gfdgdxi.top/VFP9SP1RT.EXE", "VFP9SP1RT.EXE"],
        ["9.0 Runtime Service Pack 2 with Hotfixes", "http://foxpro.wine-runner.gfdgdxi.top/VFP9SP2RT.EXE", "VFP9SP2RT.EXE"]
    ]
def Download(wineBotton: str, id: int, wine: str) -> int:
    try:
        os.remove(f"/tmp/deepin-wine-runner-FoxPro/{netList[id][2]}")
    except:
        pass
    os.system(f"aria2c -x 16 -s 16 -d '/tmp/deepin-wine-runner-FoxPro' -o '{netList[id][2]}' \"{netList[id][1]}\"")
    return os.system(f"WINEPREFIX='{wineBotton}' {wine} '/tmp/deepin-wine-runner-FoxPro/{netList[id][2]}'")

if __name__ == "__main__":
    if "--help" in sys.argv:
        print("作者：gfdgd xi")
        print("版本：1.0.0")
        print("本程序可以更方便的在 wine 容器中安装 Visual FoxPro")
        sys.exit()
    if len(sys.argv) <= 2 or sys.argv[1] == "" or sys.argv[2] == "":
        print("您未指定需要安装 Visual FoxPro 的容器和使用的 wine，无法继续")
        print("参数：")
        print("XXX 参数一 参数二 参数三(可略)")
        print("参数一为需要安装的容器，参数二为需要使用的wine，参数三为是否缓存（可略），三个参数位置不能颠倒")
        sys.exit()

    homePath = os.path.expanduser('~')
    print('''                                          
 mmmmmm               mmmmm               
 #       mmm   m   m  #   "#  m mm   mmm  
 #mmmmm #" "#   #m#   #mmm#"  #"  " #" "# 
 #      #   #   m#m   #       #     #   # 
 #      "#m#"  m" "m  #       #     "#m#" 
                                          
                                          
''')

    print("请选择以下的 Visual FoxPro 进行安装（不保证能正常安装运行）")
    for i in range(0, len(netList)):
        print(f"{i} Visual FoxPro {netList[i][0]}")
    while True:
        try:
            choose = input("请输入要选择的 Visual FoxPro 版本（输入“exit”退出）：").lower()
            if choose == "exit":
                break
            choose = int(choose)
        except:
            print("输入错误，请重新输入")
            continue
        if 0 <= choose and choose < len(netList):
            break
    if choose == "exit":
        exit()
    print(f"您选择了 Visual FoxPro {netList[choose][0]}")
    if os.path.exists(f"{homePath}/.cache/deepin-wine-runner/vcpp/{netList[choose][2]}"):
        print("已经缓存，使用本地版本")
        os.system(f"WINEPREFIX='{sys.argv[1]}' {sys.argv[2]} '{homePath}/.cache/deepin-wine-runner/vcpp/{netList[choose][2]}'")
        input("安装结束，按回车键退出")
        exit()
    print("开始下载")
    os.system(f"rm -rf '{homePath}/.cache/deepin-wine-runner/vcpp/{netList[choose][2]}'")
    os.system(f"mkdir -p '{homePath}/.cache/deepin-wine-runner/vcpp'")
    os.system(f"aria2c -x 16 -s 16 -d '{homePath}/.cache/deepin-wine-runner/vcpp' -o '{netList[choose][2]}' \"{netList[choose][1]}\"")
    os.system(f"WINEPREFIX='{sys.argv[1]}' {sys.argv[2]} '{homePath}/.cache/deepin-wine-runner/vcpp/{netList[choose][2]}'")
    input("安装结束，按回车键退出")