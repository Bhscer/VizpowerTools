import requests
import time
import hashlib
import os
import win32api
import uuid,re
import json
import datetime
import base64
from configparser import ConfigParser
import subprocess

app_version = 1.01

r = requests.get("https://bhscer.github.io/wxb_py/files/app_info_noGUI.json")
update_file_name = "app_info_noGUI.json"
with open(update_file_name, "wb") as code:
    code.write(r.content)
with open("app_info.json", 'r') as f:
    a = json.load(f)
if a['avliable'] == 1:
    if a['newest_version'] != app_version:
        app_v_newest = a['newest_version']
        app_newest = 0
        if a['must_update'] == 1:
            print("检测到新版本")
            print("该版本为强制更新版本")
            print("更新日志如下")
            print(a['update_log'])
            input("按任意键开始更新...")
        elif a['must_update'] == 0:
            print("检测到新版本")
            print("更新日志如下")
            print(a['update_log'])
            update_flag = input("按y开始更新 n下次更新")
            if update_flag == "y":
               print("update start")#update start
            elif update_flag == "n":
               print("update stopped")#update stopped
    else:
        app_newest = 1
elif a['avliable'] == 0:
    print(a['close_message'])
    input("按任意键退出...")
    End
os.remove(update_file_name)
    
#判断wxb是否存在
windirdisk = (os.getenv("windir"))[0:3]
if os.path.exists(windirdisk + "ProgramData\Microsoft\Windows\Start Menu\Programs\无限宝"):
    if os.path.exists(windirdisk + "Program Files (x86)\wxb"):
        imeetingpath = windirdisk + "Program Files (x86)\wxb\iMeeting.exe"
        #print("发现imeeting文件：" + imeetingpath)
    elif os.path.exists(windirdisk + "Program Files\wxb"):
        imeetingpath = windirdisk + "Program Files\wxb\iMeeting.exe"
        #print("发现imeeting文件：" + imeetingpath)
    else:
        print("很抱歉，我们找不到您的无限宝所在位置" + "\n" + "请尝试把本软件复制到无限宝目录中并再次打开")
        imeetingpath_1 = input("或者在此处输入您的imeeting文件所在位置： ")
        if os.path.exists(imeetingpath_1):
            imeetingpath = imeetingpath_1
        else:
            print("输入的路径不存在")
            input("press enter to exit.")
elif os.path.exists("iMeeting.exe"):
    imeetingpath = "iMeeting.exe"
    print("发现imeeting文件：" + imeetingpath)
else:
    print("很抱歉，我们找不到您的无限宝所在位置" + "\n" + "请尝试重新安装无限宝" + "\n" + "或尝试把本软件复制到无限宝目录中并再次打开")
    imeetingpath_1 = input("或者在此处输入您的imeeting文件所在位置： ")
    if os.path.exists(imeetingpath_1):
        imeetingpath = imeetingpath_1
    else:
        print("输入的路径不存在")
        input("press enter to exit.")
remembered = 0

if os.path.exists("user_info.txt"):
    f = open("user_info.txt",'r', encoding='UTF-8')
    r_text = f.readlines()[0]     #读取内容
f.close
if os.path.exists("user_info.txt") and (os.path.getsize("user_info.txt")) != 0 and ("£" in r_text) and ("¢" in r_text) and ("∆" in r_text):  #存在密码文件
    n = 1
    uid_time = 0
    pwd_time = 0
    while n <= len(r_text):
            r_search_tmp = r_text[n:n+1]
            if r_search_tmp == "£":    #读取域名
                r_prefix_end = n
                prefix = r_text[1:n]
            if r_search_tmp == "¢":    #读取账号
                uid_time = uid_time + 1
                r_uid_end = 0
                r_uid_start = r_prefix_end + 2
                if uid_time == 2:
                    r_uid_end = n
                user_name = r_text[r_uid_start:r_uid_end]
            if r_search_tmp == "∆":    #读取密码
                pwd_time = pwd_time + 1
                r_pwd_end = 0
                r_pwd_start = r_uid_end + 2
                if pwd_time == 2:
                    r_pwd_end = n
                password = r_text[r_pwd_start:r_pwd_end]
            n = n + 1
    #print("发现已保存的信息，正在登录")
    remembered = 1
else:
    prefix = input("Server prefix (example: the prefix for cc.kehou.com is \"cc\"): ")
    user_name = input("Username: ")
    password = input("Password: ")

#取 MD5
def string_to_md5(string):
    h = hashlib.md5()
    h.update(string.encode("utf-8"))
    return h.hexdigest()
#ping
def getPING(domain):
    ''' 调用系统自带的ping.exe实现PING domain，返回值为：ip,丢包率,最短，最长，平均'''
    p = subprocess.Popen(["ping.exe", domain], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
    out = p.stdout.read().decode('gbk')
    regIP = r'\[\d+\.\d+\.\d+\.\d+\]'               ## Pinging www.a.shifen.com [115.239.211.112] with 32 bytes of data
    regLost = r'\(\d+%'                             ## Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)   数据包: 已发送 = 4，已接收 = 4，丢失 = 0 (0% 丢失)，
    regMinimum = u'Minimum = \d+ms|最短 = \d+ms'     ## Minimum = 37ms, Maximum = 38ms, Average = 37ms   最短 = 37ms，最长 = 77ms，平均 = 48ms
    regMaximum = u'Maximum = \d+ms|最长 = \d+ms'
    regAverage = u'Average = \d+ms|平均 = \d+ms'
    ip = re.search(regIP, out)
    lost = re.search(regLost, out)
    minimum = re.search(regMinimum, out)
    maximum = re.search(regMaximum, out)
    average = re.search(regAverage, out)
    if ip:
        ip = ip.group()[1:-1]
    if lost:
        lost = lost.group()[1:]
    if minimum:
        minimum = filter(lambda x:x.isdigit(),minimum.group())
    if maximum:
        maximum = filter(lambda x:x.isdigit(),maximum.group())
    if average:
        average = filter(lambda x:x.isdigit(),average.group())
    #return (ip,lost,minimum,maximum,average)
    return (maximum)
#获取wxb回复
def get_wxb_response():
    salt = str(int(time.time()))
    pwd = string_to_md5(user_name + password + salt + "WINUPON")
    pwd2 = string_to_md5(user_name + string_to_md5(password) + salt + "WINUPON")
    device_mac = uuid.uuid1().hex[-12:].upper()
    device_mac = ":".join(re.findall(r".{2}", device_mac))
    url_final = "http://" + prefix + ".kehou.com/courseList.action?uid=" + user_name + "&pwd=" + pwd + "&pwd2=" + pwd2 + "&salt=" + salt + "&callfrom=vplogintool&mac=" + device_mac
    url_final = url_final.replace(" ", "")
    #print(url_final)
    r = requests.get(url_final)
    file_name = "wxb_response.ini"
    with open(file_name, "wb") as code:
        code.write(r.content)
#读取wxb回复内容
def info_reader():
    class_enter_name = "[mt" + attend_class_number + "]"
    cfg = ConfigParser()
    cfg.read(file_name)
    MeetId = cfg.get(class_enter_name, 'MeetId')
    timesId = cfg.get(class_enter_name, 'timesId')
    Meeting_Subject = cfg.get(class_enter_name, 'Meeting-Subject')
    MeetCurrTime = cfg.get(class_enter_name, 'MeetCurrTime')
    Meeting_Duration = cfg.get(class_enter_name, 'Meeting-Duration')
    EastimateTime = cfg.get(class_enter_name, 'EastimateTime')
    MeetStartTime = cfg.get(class_enter_name, 'MeetStartTime')
    Meeting_Chairman = cfg.get(class_enter_name, 'Meeting-Chairman')
    Meeting_Project = cfg.get(class_enter_name, 'Meeting-Project')
    Meeting_BeforeTime = cfg.get(class_enter_name, 'Meeting-BeforeTime')
    userId = cfg.get(class_enter_name, 'userId')
    NickName = cfg.get(class_enter_name, 'NickName')
    Course_Big_PictureUrl = cfg.get(class_enter_name, 'Course-Big-PictureUrl')
    Course_Total_time = cfg.get(class_enter_name, 'Course-Total-time')
    WinAppTitle = cfg.get(class_enter_name, 'WinAppTitle')
    ProjectName = cfg.get(class_enter_name, 'ProjectName')
    NeedSSR = cfg.get(class_enter_name, 'NeedSSR')
    ServerIP = cfg.get(class_enter_name, 'ServerIP')
    Port = cfg.get(class_enter_name, 'Port')
    AutoRecordPrompt = cfg.get(class_enter_name, 'AutoRecordPrompt')
    Meeting_AddTime = cfg.get(class_enter_name, 'Meeting-AddTime')
    ClientType = cfg.get(class_enter_name, 'ClientType')
    ProxyAllocType = cfg.get(class_enter_name, 'ProxyAllocType')
    MultiMeeting = cfg.get(class_enter_name, 'MultiMeeting')
    listenType = cfg.get(class_enter_name, 'listenType')
    MeetingQuitURL = cfg.get(class_enter_name, 'MeetingQuitURL')
    PresidentKey2 = cfg.get(class_enter_name, 'PresidentKey2')
    VerifyKey = cfg.get(class_enter_name, 'VerifyKey')
    signupCount = cfg.get(class_enter_name, 'signupCount')
    SnapUploadURL = cfg.get(class_enter_name, 'SnapUploadURL')
    RestVodURL = cfg.get(class_enter_name, 'RestVodURL')
    QRCodeBaseURL = cfg.get(class_enter_name, 'QRCodeBaseURL')
    ClassNoteURL = cfg.get(class_enter_name, 'ClassNoteURL')
    StuSchool = cfg.get(class_enter_name, 'StuSchool')
    StuClass = cfg.get(class_enter_name, 'StuClass')
    StuPhone = cfg.get(class_enter_name, 'StuPhone')
    CameraRemind = cfg.get(class_enter_name, 'CameraRemind')
    CameraSnap = cfg.get(class_enter_name, 'CameraSnap')
    NDConf = cfg.get(class_enter_name, 'NDConf')
    ShowUserCount = cfg.get(class_enter_name, 'ShowUserCount')
    ClassAutoLock = cfg.get(class_enter_name, 'ClassAutoLock')
    IPVCamera = cfg.get(class_enter_name, 'IPVCamera')
    VideoQualityLevel = cfg.get(class_enter_name, 'VideoQualityLevel')
    AllowHLS = cfg.get(class_enter_name, 'AllowHLS')
    NetDiskProtocol = cfg.get(class_enter_name, 'NetDiskProtocol')
    NetDiskUploadURL = cfg.get(class_enter_name, 'NetDiskUploadURL')
    NetDiskNotifyURL = cfg.get(class_enter_name, 'NetDiskNotifyURL')
    NetDiskUserName = cfg.get(class_enter_name, 'NetDiskUserName')
    NetDiskUserPasswd = cfg.get(class_enter_name, 'NetDiskUserPasswd')
    RecordBlackList = cfg.get(class_enter_name, 'RecordBlackList')
    EvaluateURL = cfg.get(class_enter_name, 'EvaluateURL')
    DocURL = cfg.get(class_enter_name, 'DocURL')
    GreenScreenURL = cfg.get(class_enter_name, 'GreenScreenURL')
    FeedbackURL = cfg.get(class_enter_name, 'FeedbackURL')
    MultiVideoChannels = cfg.get(class_enter_name, 'MultiVideoChannels')
    EditTestStdAns = cfg.get(class_enter_name, 'EditTestStdAns')
    STick = cfg.get(class_enter_name, 'STick')
    SKey = cfg.get(class_enter_name, 'SKey')
#生成wxb启动指令
def shell_maker():
    # s_t = shell_head r_s = run_shell
    s_t = "</94AEB546-26AE-48da-AC3A-B15BF1245699><94AEB546-26AE-48da-AC3A-B15BF1245699"
    r_s = "<94AEB546-26AE-48da-AC3A-B15BF1245699AllowHLS>" + AllowHLS + s_t + "AutoRecordPrompt>" + AutoRecordPrompt + s_t + "CameraRemind>" + CameraRemind + s_t + "CameraSnap>" + CameraSnap
    r_s = r_s + s_t + "ClassAutoLock>" + ClassAutoLock + s_t + "ClassNoteURL>" + ClassNoteURL + s_t + "ClientType>" + ClientType + s_t + "Course-Big-PictureUrl>" + Course_Big_PictureUrl
    r_s = r_s + s_t + "Course-Total-time>" + Course_Total_time + s_t + "DocURL>" + DocURL + s_t + "EastimateTime>" + EastimateTime + s_t + "EditTestStdAns>" + EditTestStdAns
    r_s = r_s + s_t + "EvaluateURL>" + EvaluateURL + s_t + "FeedbackURL>" + FeedbackURL + s_t + "GreenScreenURL>" + GreenScreenURL + s_t + "IPVCamera>" + IPVCamera + s_t + "MeetCurrTime>" + MeetCurrTime
    r_s = r_s + s_t + "MeetId>" + MeetId + s_t + "MeetStartTime>" + MeetStartTime + s_t + "Meeting-AddTime>" + Meeting_AddTime + s_t + "Meeting-BeforeTime>" + Meeting_BeforeTime
    r_s = r_s + s_t + "Meeting-Chairman>" + Meeting_Chairman + s_t + "Meeting-Duration>" + Meeting_Duration + s_t + "Meeting-Project>" + Meeting_Project + s_t + "Meeting-Subject>" + Meeting_Subject
    r_s = r_s + s_t + "MeetingQuitURL>" + MeetingQuitURL + s_t + "MultiMeeting>" + MultiMeeting + s_t + "MultiVideoChannels>" + MultiVideoChannels + s_t + "NDConf>" + NDConf
    r_s = r_s + s_t + "NeedSSR>" + NeedSSR + s_t + "NetDiskNotifyURL>" + NetDiskNotifyURL + s_t + "NetDiskProtocol>" + NetDiskProtocol + s_t + "NetDiskUploadURL>" + NetDiskUploadURL
    r_s = r_s + s_t + "NetDiskUserName>" + NetDiskUserName + s_t + "NetDiskUserPasswd>" + NetDiskUserPasswd + s_t + "NickName>" + NickName + s_t + "Port>" + Port
    r_s = r_s + s_t + "PresidentKey2>" + PresidentKey2 + s_t + "ProjectName>" + ProjectName + s_t + "ProxyAllocType>" + ProxyAllocType + s_t + "QRCodeBaseURL>" + QRCodeBaseURL
    r_s = r_s + s_t + "RecordBlackList>" + RecordBlackList + s_t + "RestVodURL>" + RestVodURL + s_t + "SKey>" + SKey + s_t + "STick>" + STick + s_t + "ServerIP>" + ServerIP
    r_s = r_s + s_t + "ShowUserCount>" + ShowUserCount + s_t + "SnapUploadURL>" + SnapUploadURL + s_t + "StuClass>" + StuClass + s_t + "StuPhone>" + StuPhone
    r_s = r_s + s_t + "StuSchool>" + StuSchool + s_t + "VerifyKey>" + VerifyKey + s_t + "VideoQualityLevel>" + VideoQualityLevel + s_t + "WinAppTitle>" + WinAppTitle
    r_s = r_s + s_t + "exeurl>" + exeurl + s_t + "listenType>" + listenType + s_t + "signupCount>" + signupCount + s_t + "timesId>" + timesId
    r_s = r_s + s_t + "updatedirurl>" + updatedirurl + s_t + "userId>" + userId + "</94AEB546-26AE-48da-AC3A-B15BF1245699>"
    r_s = r_s.replace("\n", "")
#自动上课
def auto_class():
    now_time = datetime.time(1, 6, 30)
    print("时：", now_time.hour)
    print("分：", now_time.minute)
    print("秒：", now_time.second)
    print("微秒：", now_time.microsecond)
    if (now_time.hour == 7 and now_time.minute >= 45) or (7 < now_time.hour < 16) or (
            now_time.hour == 16 and now_time.minute >= 25):
        # 时间符合
        if int(class_ing_number) == 1:  # 一节课
            attend_class_number = 1
            class_info_line_start = 21 + line_count_2 + 59 * (int(attend_class_number) - 1) + 1
            class_info_line_end = 21 + line_count_2 + 59 * int(attend_class_number)
            # print(class_info_line_start)
            # print(class_info_line_end)
            search_count = class_info_line_start
            while search_count <= class_info_line_end:
                f = open(file_name)
                # l_tmp = search_line_count
                l_tmp = f.readlines()[search_count]
                f.close
                search_count = search_count + 1
                if "Meeting-Duration" in l_tmp:
                    Meeting_Duration = l_tmp[17:]
            class_start_hour = Meeting_Duration[0:1]
            class_start_minute = Meeting_Duration[3:4]
            class_end_hour = Meeting_Duration[6:7]
            class_end_minute = Meeting_Duration[9:10]
            if int(class_start_hour + class_start_minute) <= int(
                    now_time.hour + now_time.minute) <= int(class_end_hour + class_end_minute):
                print("22")  # 在上课了
            elif int(class_start_hour + class_start_minute) >= int(
                    now_time.hour + now_time.minute):
                # 还没上课
                # 上课
                print("进入课堂...")
        if int(class_ing_number) > 1:  # 一节课以上
            if int(class_ing_number) == 2:
                attend_class_number = 1
                class1_info_line_start = 21 + line_count_2 + 59 * (
                        int(attend_class_number) - 1) + 1
                class1_info_line_end = 21 + line_count_2 + 59 * int(attend_class_number)
                # print(class_info_line_start)
                # print(class_info_line_end)
                search_count = class_info_line_start
                while search_count <= class_info_line_end:
                    f = open(file_name)
                    # l_tmp = search_line_count
                    l_tmp = f.readlines()[search_count]
                    f.close
                    search_count = search_count + 1
                    if "Meeting-Duration" in l_tmp:
                        Meeting_Duration1 = l_tmp[17:]
                class1_start_hour = Meeting_Duration1[0:1]
                class1_start_minute = Meeting_Duration1[3:4]
                class1_end_hour = Meeting_Duration1[6:7]
                class1_end_minute = Meeting_Duration1[9:10]

                attend_class_number = 2
                class1_info_line_start = 21 + line_count_2 + 59 * (
                        int(attend_class_number) - 1) + 1
                class1_info_line_end = 21 + line_count_2 + 59 * int(attend_class_number)
                # print(class_info_line_start)
                # print(class_info_line_end)
                search_count = class_info_line_start
                while search_count <= class_info_line_end:
                    f = open(file_name)
                    # l_tmp = search_line_count
                    l_tmp = f.readlines()[search_count]
                    f.close
                    search_count = search_count + 1
                    if "Meeting-Duration" in l_tmp:
                        Meeting_Duration2 = l_tmp[17:]
                class2_start_hour = Meeting_Duration2[0:1]
                class2_start_minute = Meeting_Duration2[3:4]
                class2_end_hour = Meeting_Duration2[6:7]
                class2_end_minute = Meeting_Duration2[9:10]

                if int(class_start_hour + class_start_minute) <= int(
                        now_time.hour + now_time.minute) <= int(
                    class_end_hour + class_end_minute):
                    print("22")  # 在上课了
                elif int(class_start_hour + class_start_minute) >= int(
                        now_time.hour + now_time.minute):
                    # 还没上课
                    # 上课
                    print("进入课堂...")

file_name = "wxb_response.ini"

while 1 == 1:

    print("无限宝登录工具 v" + str(app_version))
    print("***************\n"
          "\n"
          "1.单门上课\n"
          "2.自动上课\n"
          "3.用户信息\n"
          "4.账号管理\n"
          "5.软件设置\n"
          "\n"
          "***************\n")
    main_choice = input("输入你的指令: ")

    if main_choice == "1":
        print("正在登录")
        salt = str(int(time.time()))
        pwd = string_to_md5(user_name + password + salt + "WINUPON")
        pwd2 = string_to_md5(user_name + string_to_md5(password) + salt + "WINUPON")
        device_mac = uuid.uuid1().hex[-12:].upper()
        device_mac = ":".join(re.findall(r".{2}", device_mac))
        url_final = "http://" + prefix + ".kehou.com/courseList.action?uid=" + user_name + "&pwd=" + pwd + "&pwd2=" + pwd2 + "&salt=" + salt + "&callfrom=vplogintool&mac=" + device_mac
        url_final = url_final.replace(" ", "")
        # print(url_final)
        r = requests.get(url_final)
        file_name = "wxb_response.ini"
        with open(file_name, "wb") as code:
            code.write(r.content)
        f = open(file_name)
        r_line2 = f.readlines()[2]
        f.close
        # 读取行数
        line_count = 0
        f = open(file_name, "r")
        for line in f.readlines():
            line_count = line_count + 1
        f.close

        # 分析
        if "[error]" in r_line2:
            f = open(file_name)
            r_line3 = f.readlines()[3]
            f = open(file_name)
            r_line4 = f.readlines()[4]
            print("发生错误 " + r_line3[6:] + r_line4[8:])
        elif "[userinfo1]" in r_line2:
            print("您没有正在上的课哦")
        elif "[update]" in r_line2:
            print("登陆成功")
            # 保存账号密码etc.
            w_prefix = "£" + prefix + "£"
            w_user_name = "¢" + user_name + "¢"
            w_password = "∆" + password + "∆"
            f = open("user_info.txt", 'w', encoding='UTF-8')
            f.write(w_prefix + w_user_name + w_password)
            f.close
            f = open(file_name)
            class_ing_text1 = (f.readlines()[18])[5:]
            f.close
            # print(len(class_ing_text1))
            class_ing_number = 0
            if len(class_ing_text1) == 2:
                class_ing_number = 1
            elif 3 <= len(class_ing_text1) <= 17:
                class_ing_number = ((len(class_ing_text1)) / 2)
            elif len(class_ing_text1) > 17:
                class_ing_number = 9 + (((len(class_ing_text1) - 18)) / 3)
            if class_ing_number == 0:
                print("您没有正在上的课哦")
            else:
                print(" ")
                print("您现在有 " + str(int(class_ing_number)) + " 节直播课")
                print(" ")
                line_count_1 = 0
                line_count_2 = 0
                while line_count_1 < line_count:
                    f = open(file_name)
                    if "mtname" in (f.readlines()[line_count_1]):
                        if line_count_2 < 8:
                            if (line_count_2 + 1) <= class_ing_number:
                                f = open(file_name)
                                print(str(line_count_2 + 1) + " " + ((f.readlines()[line_count_1])[8:]))
                        elif line_count_2 > 8:
                            if (line_count_2 + 1) <= class_ing_number:
                                f = open(file_name)
                                print(str(line_count_2 + 1) + " " + ((f.readlines()[line_count_1])[9:]))
                        line_count_2 = line_count_2 + 1
                    line_count_1 = line_count_1 + 1
                attend_class_number = input("输入您要上的课序号: ")
                if int(attend_class_number) <= class_ing_number:
                    # print(line_count_2)
                    info_reader()
                    print(" ")
                    sif_dontlockclass = input("是否取消自动锁定课堂？ （y/n）")
                    if ("y" in sif_dontlockclass) or ("Y" in sif_dontlockclass):
                        ClassAutoLock = "0"
                    elif ("n" in sif_dontlockclass) or ("N" in sif_dontlockclass):
                        ClassAutoLock = "1"
                    sif_showonlinecount = input("是否显示课堂在线人数？ （y/n）")
                    if ("y" in sif_showonlinecount) or ("Y" in sif_showonlinecount):
                        ShowUserCount = "1"
                    elif ("n" in sif_showonlinecount) or ("N" in sif_showonlinecount):
                        ShowUserCount = "1"
                    sif_recordallowed = input("是否解除录屏限制？ （y/n）")
                    if ("y" in sif_recordallowed) or ("Y" in sif_recordallowed):
                        RecordBlackList = ""
                    print("开始生成shell命令")
                    f = open(file_name)
                    updatedirurl = (f.readlines()[3])[13:]
                    f.close
                    f = open(file_name)
                    exeurl = (f.readlines()[6])[7:]
                    f.close
                    shell_maker()
                    print("shell命令生成成功")
                    print("正在启动无限宝")
                    #f = open("wxb_shell.txt", "w")
                    #f.write(r_s)
                    #f.close()
                    #os.startfile("wxb_open.exe")
                    win32api.ShellExecute(0, 'open',imeetingpath,r_s, '', 1)
                    # win32api.ShellExecute(0, 'open',"wxb_open.exe",'', '', 1)

                else:
                    print("你输入的内容有误")
        else:
            print("与服务器联系失败")

        input("按任意键返回主菜单...")

    elif main_choice == "2":
        print("自动上课")
        print("Devloping...")

        #t = Timer(10.0, auto_class)
        #t.start()

    elif main_choice == "3":
        # 信息
        get_wxb_response()

        f = open(file_name)
        r_line2 = f.readlines()[2]
        f.close
        # 读取行数
        line_count = 0
        f = open(file_name, "r")
        for line in f.readlines():
            line_count = line_count + 1
        f.close

        cfg = ConfigParser()
        cfg.read(file_name)
        # print(cfg.sections())
        # print(cfg.get('userinfo1', 'name'))
        # 分析
        if "[error]" in r_line2:
            f = open(file_name)
            r_line3 = f.readlines()[3]
            f = open(file_name)
            r_line4 = f.readlines()[4]
            print("发生错误 " + r_line3[6:] + r_line4[8:])
        elif "[userinfo1]" in r_line2 or "[update]" in r_line2:
            webuserid = cfg.get('userinfo1', 'webuserid')
            user_name = cfg.get('userinfo1', 'username')
            name = cfg.get('userinfo1', 'name')
            unit = cfg.get('userinfo1', 'unit')
            class_name = cfg.get('userinfo1', 'classname')
            role = cfg.get('userinfo1', 'role')
            f = open(file_name)
            webuserid = (f.readlines()[3])[10:]
            webuserid_1 = webuserid.encode("utf-8")
            s_userid = base64.b64encode(webuserid_1)
            s_userid = str(s_userid, 'utf-8')
            # print(s_userid)
            # s_userid = base64.b64encode(str(webuserid_1))  # base64加密
            # base64.b64decode("YWFh")  # base64解密
            s_userid = string_to_md5(s_userid)
            white_list = requests.get("https://bhscer.github.io/wxb_py/files/white_list.txt")
            # print(white_list.content.decode(r.encoding))
            if s_userid in (white_list.content.decode(r.encoding)):
                s_allowed_flag = "已授权"
            else:
                s_allowed_flag = "未授权"
            print(name.replace("\n",
                               "") + " " + role + "\n" + unit + "\n" + class_name + "\n" + user_name + "\n" + "s_id:" + s_userid.replace(
                "\n", "") + " （" + s_allowed_flag + "）")
            input("按任意键返回主菜单...")
        else:
            print("与服务器联系失败")

    elif main_choice == "4":
        if os.path.exists("user_info.txt"):
            f = open("user_info.txt", 'r', encoding='UTF-8')
            r_text = f.readlines()[0]  # 读取内容
            f.close

        if os.path.exists("user_info.txt") and (os.path.getsize("user_info.txt")) != 0 and ("£" in r_text) and (
                "¢" in r_text) and ("∆" in r_text):  # 存在密码文件
            n = 1
            uid_time = 0
            pwd_time = 0
            while n <= len(r_text):
                r_search_tmp = r_text[n:n + 1]
                if r_search_tmp == "£":  # 读取域名
                    r_prefix_end = n
                    prefix = r_text[1:n]
                if r_search_tmp == "¢":  # 读取账号
                    uid_time = uid_time + 1
                    r_uid_end = 0
                    r_uid_start = r_prefix_end + 2
                    if uid_time == 2:
                        r_uid_end = n
                    user_name = r_text[r_uid_start:r_uid_end]
                if r_search_tmp == "∆":  # 读取密码
                    pwd_time = pwd_time + 1
                    r_pwd_end = 0
                    r_pwd_start = r_uid_end + 2
                    if pwd_time == 2:
                        r_pwd_end = n
                    password = r_text[r_pwd_start:r_pwd_end]
                n = n + 1
            # print("发现已保存的信息，正在登录")
            print("域名：" + prefix)
            print("账号：" + user_name)
            input("按任意键返回主菜单...")

    elif main_choice == "5":
        if app_newest == 1:
            app_update_info = "（最新版）"
        else:
            app_update_info = "（最新为" + str(app_v_newest) + "）"
        print("app版本：" + str(app_version) + app_update_info +"noGUI version")
        print("imeeting文件：" + imeetingpath)
        print("Powered by Python")
        print("https://github.com/Bhscer/VizpowerTools")
        #print(list(getPING("www.baidu.com")))
        input("按任意键返回主菜单...")

#os.remove(file_name)

