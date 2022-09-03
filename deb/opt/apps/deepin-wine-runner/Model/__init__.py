import os
def OpenTerminal(command):
    if terminalEnd[terminal][1]:
        os.system(f"\"{terminal}\" \"{terminalEnd[terminal][0]}\" \"{command}\"")
        return
    os.system(f"\"{terminal}\" \"{terminalEnd[terminal][0]}\" {command}")
programPath = os.path.split(os.path.realpath(__file__))[0]  # 返回 string
# 对终端的获取
# 为什么 openkylin 只有 mate-terminal
# 优先为深度终端
terminal = ""
terminalList = [
    "deepin-terminal1",
    "mate-terminal1",
    "gnome-terminal"
]
terminalEnd = {
    f"{programPath}/launch.sh\" \"deepin-terminal": ["-e", 0],
    "mate-terminal": ["-e", 1],
    "gnome-terminal": ["--", 0]
}
for i in terminalList:
    if not os.system(f"which {i}"):
        if i == "deepin-terminal":
            i = f"{programPath}/launch.sh\" \"deepin-terminal"
        terminal = i
        break
if terminal == "":
    print("无法识别到以下的任意一个终端")
    print(" ".join(terminalList))
    exit()