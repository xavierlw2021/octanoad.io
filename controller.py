#2022.05.14 封裝ver.3.1 youtube更動, pytube改版, 新增網址多餘參數去除, 使用pytube內建includes_audio_track檢測音訊串流
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from pytube import YouTube 
import os, re, subprocess, time
from subprocess import Popen
from UI import Ui_MainWindow

class MainWindow_controller(QMainWindow):
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()

    def setup_control(self):
        choice = ['MP3', 'MP4(480p)', 'MP4(720p)', 'MP4(1080p)']    #輸出類型選項 
        self.ui.option_1.addItems(choice) 
        self.ui.option_2.addItems(choice) 
        self.ui.option_3.addItems(choice) 
        self.ui.option_4.addItems(choice) 
        self.ui.option_5.addItems(choice) 
        self.ui.option_6.addItems(choice) 
        self.ui.option_7.addItems(choice) 
        self.ui.option_8.addItems(choice)
        self.ui.msg_label.setText('(1)請於各序列輸入網址 (2)注意!!輸出路徑不可含有中文')
        self.ui.folder_Button.clicked.connect(self.open_folder) #資料夾選擇按鈕
        self.ui.checkButton.clicked.connect(self.use_pytube)    #開始執行

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open folder", "./")
        self.ui.file_output.setText(folder_path)

    def on_Progress(self, stream, chunk, remaining): 
        total = stream.filesize
        percent = (total - remaining) / total * 100
        print(f'Downloading...{percent:05.2f}%\r')
 
    def download_audio(self, filters, new_name, src):
        audio_list = filters(type = 'audio').all
        strf = str(audio_list).find   #簡寫
        l1 = re.split(',' , str(audio_list)[strf('[')+1 : strf(']')])   #取得音訊list
        l2 = [int(s[s.find('abr="')+5 : s.find('kbps"')]) for s in l1]  #取得音訊數值list
        try:
            target = filters(abr = f'{max(l2)}kbps' , type = 'audio').first()
            abr_=max(l2)
        except:
            target = filters(abr = '128kbps' , type = 'audio').first()
            abr_=128
        o_title , e = os.path.splitext(target.default_filename)
        target.download(output_path = src,  filename = f'{new_name}{e}')  #執行下載
        return e , abr_ , o_title

    def mp3_change(self, src, name, ext, abr_):
        file_name = f'{name}{ext}'
        if ext.lower() in ('.mp4', '.m4a', '.flac' , '.webm'):
            file = os.path.join(src, file_name)  #組裝為來源路徑
            name = os.path.join(src, name)  #組裝為輸出路徑
            os.system('ffmpeg -i "{0}" -vn -ab {1} "{2}.mp3"'.format(file, abr_, name))
            os.remove(file)

    def download_video(self, filters, new_name, option, src):          
        target = filters(res = option[4:-1], mime_type = 'video/mp4').first()
        if target == None:  #避免上述畫質不存在，進行例外處理
            print('該畫質選項不存在, 將下載預設影片')
            target = filters(mime_type = 'video/mp4').first()
        o_title , e = os.path.splitext(target.default_filename)
        target.download(output_path = src,  filename = f'{new_name}{e}')  #執行下載   
        if target.includes_audio_track == False:        
            print('該影片未含有音訊, 自動下載音訊並合併')
            self.mix_video(filters, src, new_name, e)
        # return e , o_title
        return o_title

    def analysis_audio(self, src, name, ext):
        temp_video = os.path.join(src, f'{name}{ext}')
        ana = Popen(['ffprobe', temp_video], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = ana.communicate()
        return out.decode('utf-8').find('Audio')

    def mix_video(self, filters, src, name, v_ext): 
        target =filters(type = 'audio').first()
        old_name = target.default_filename
        _ , a_ext = os.path.splitext(old_name)
        target.download(output_path = src,  filename = f'bgm{a_ext}')
        
        temp_video = os.path.join(src, f'{name}{v_ext}')
        temp_audio = os.path.join(src, f'bgm{a_ext}')
        mix_file = os.path.join(src, 'mix.mp4')
        os.system('ffmpeg -i {0} -i {1} -c:v copy -c:a aac {2}'.format(temp_video, temp_audio, mix_file))
        os.remove(temp_video)
        os.remove(temp_audio)
        os.rename(mix_file, os.path.join(src, f'{name}.mp4'))

    def dlList_writer(self, d):        
        with open('download_list.txt', 'w', encoding='utf-8') as f:
            for n, o in d.items():
                f.write(f'{n}:{o}\n')            

    def use_pytube(self):
        checkrun = [self.ui.check_run_1, self.ui.check_run_2, self.ui.check_run_3, self.ui.check_run_4,
                    self.ui.check_run_5, self.ui.check_run_6, self.ui.check_run_7, self.ui.check_run_8]        

        urls = [self.ui.yt_url_input_1, self.ui.yt_url_input_2, self.ui.yt_url_input_3, self.ui.yt_url_input_4,
                self.ui.yt_url_input_5, self.ui.yt_url_input_6, self.ui.yt_url_input_7, self.ui.yt_url_input_8]

        option = [self.ui.option_1, self.ui.option_2, self.ui.option_3, self.ui.option_4,
                self.ui.option_5, self.ui.option_6, self.ui.option_7, self.ui.option_8]
        
        fns = [self.ui.fileName_input_1, self.ui.fileName_input_2, self.ui.fileName_input_3, self.ui.fileName_input_4,
                self.ui.fileName_input_5, self.ui.fileName_input_6, self.ui.fileName_input_7, self.ui.fileName_input_8]

        output_path = self.ui.file_output.toPlainText()
        
        reduc_name_dict = {}    #序列名稱備忘錄
        for n, c, u, o, f in zip(range(1,9), checkrun, urls, option, fns):
            if c.isChecked():
                time.sleep(5)
                print(f'序列{n}開始下載')            
                try:
                    url_keyin = u.toPlainText()
                    url_rmk = (url_keyin[:(url_keyin.find('&'))]) if '&' in url_keyin else url_keyin
                    yt  = YouTube(url_rmk, on_progress_callback = self.on_Progress)
                except:
                    print(f'序列{n}網址可能有錯, 將跳過此下載, 請再確認網址正確')
                    time.sleep(2)
                    continue

                try:
                    o = o.currentText()
                except:
                    print(f'序列{n}選項錯誤, 將跳過此下載')
                    time.sleep(2)
                    continue

                try:                    
                    f = f.toPlainText()
                    if not f.isalnum():
                        f = f'file{n}'
                        print(f'檔名未依規定, 將修改為file{n}避免轉檔錯誤。')
                except:
                    f = f'file{n}'

                ytf = yt.streams.filter   #簡寫
                if o[2] == '3': #下載音樂
                    ext, abr_, y_title = self.download_audio(ytf, f, output_path)
                    self.mp3_change(output_path, f, ext, abr_) 
                    print(f'file{n}下載並轉換mp3完成')
                elif o[2] == '4':   #下載影片
                    y_title = self.download_video(ytf, f, o, output_path)
                    # ext = self.download_video(ytf, f, o, output_path)
                    # ana = self.analysis_audio(output_path, f, ext)
                    # if ana == -1:
                    #     self.ui.msg_label.setText('該影片未含有音訊, 自動下載音訊並合併')
                    #     self.mix_video(ytf, output_path, f, ext) 
                    print(f'file{n}下載並轉換mp4完成')
                else:                    
                    self.ui.msg_label.setText('儲存選項錯誤')
                    time.sleep(2)
                    continue
                reduc_name_dict[f] = y_title

            else:
                continue        
        
        self.dlList_writer(reduc_name_dict) #建立下載備忘錄
        self.ui.msg_label.setText('下載全數完成')
