import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QProgressBar, QLabel, QScrollArea, QFileDialog, QTextBrowser
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import cv2
import numpy as np
import pydicom as pdcm
from pydicom.pixel_data_handlers.util import apply_voi_lut
import configparser
import getpass
import os

class Cropper(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        #region 0. initialization
        self.setWindowTitle('DICOM CROPPER')
        self.setWindowIcon(QIcon('./bin/icon.png'))

        config = configparser.ConfigParser()
        config.read('./bin/config.ini', encoding='utf-8')
        config.sections()

        load_root = config['root']['load_dir']
        save_root = config['root']['save_dir']

        #endregion

        #region 1.load UI
        global load_qle, save_qle

        load_qle = QLabel('', self)
        load_qle.move(20, 20)
        load_qle.resize(230, 20)
        load_qle.setDisabled(True)
        load_qle.setText(load_root)

        width = load_qle.fontMetrics().boundingRect(load_qle.text()).width()
        if width >= 230:
            load_qle.resize(width, 20)

        load_sa = QScrollArea(self)
        load_sa.resize(250, 40)
        load_sa.move(20, 20)
        load_sa.setWidget(load_qle)
        load_sa.setStyleSheet("background-color:#666666;"
                              "color : #FFFFFF;")

        load_lab = QLabel('불러올 폴더', self)
        load_lab.move(280, 20)
        load_lab.resize(100, 20)
        load_lab.setAlignment(Qt.AlignCenter)

        load_btn = QPushButton("폴더설정", self)
        load_btn.move(280, 40)
        load_btn.resize(100, 20)
        load_btn.clicked.connect(self.load_fileopen)
        #endregion

        #region 2.save UI
        save_qle = QLabel('', self)
        save_qle.move(20, 70)
        save_qle.resize(230, 20)
        save_qle.setDisabled(True)
        save_qle.setText(save_root)
        width = load_qle.fontMetrics().boundingRect(save_qle.text()).width()
        if width >= 230:
            save_qle.resize(width, 20)

        save_sa = QScrollArea(self)
        save_sa.resize(250, 40)
        save_sa.move(20, 70)
        save_sa.setWidget(save_qle)
        save_sa.setStyleSheet("background-color:#666666;"
                              "color : #FFFFFF;")

        save_lab = QLabel('내보낼 폴더', self)
        save_lab.move(280, 70)
        save_lab.resize(100, 20)
        save_lab.setAlignment(Qt.AlignCenter)

        save_btn = QPushButton("폴더설정", self)
        save_btn.move(280, 90)
        save_btn.resize(100, 20)
        save_btn.clicked.connect(self.save_fileopen)
        #endregion

        #region 3. service UI
        serv_btn = QPushButton("작업 시작", self)
        serv_btn.move(20, 265)
        serv_btn.resize(360, 20)
        serv_btn.clicked.connect(self.crop_service)

        global serv_edt
        self.serv_edt = QTextBrowser()
        self.serv_edt.move(20, 120)
        self.serv_edt.resize(355, 135)
        self.serv_edt.setDisabled(True)
        self.serv_edt.setStyleSheet( "color : #000000;"
                                "border-style : None;")
        self.serv_edt.append("작업 준비가 완료되었습니다.")

        serv_scr = QScrollArea(self)
        serv_scr.move(20, 120)
        serv_scr.resize(360, 140)
        serv_scr.setWidget(self.serv_edt)

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(0,290,440,10)
        #endregion

        #region 99. etc
        self.resize(400, 300)
        self.center()
        self.show()
        #endregion

    def save_fileopen(self):
        filepath = QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), "./", QFileDialog.ShowDirsOnly)
        config = configparser.ConfigParser()
        save_qle.setText(str(filepath))
        width = save_qle.fontMetrics().boundingRect(save_qle.text()).width()
        if width >= 230:
            save_qle.resize(width, 20)

        config['root'] = {}
        config['root']['load_dir'] = load_qle.text()
        config['root']['save_dir'] = str(filepath)
        with open('./bin/config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)


    def load_fileopen(self):
        filepath = QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), "./", QFileDialog.ShowDirsOnly)
        config = configparser.ConfigParser()
        load_qle.setText(str(filepath))
        width = load_qle.fontMetrics().boundingRect(load_qle.text()).width()
        if width >= 230:
            load_qle.resize(width, 20)

        config['root'] = {}
        config['root']['load_dir'] = str(filepath)
        config['root']['save_dir'] = save_qle.text()
        with open('./bin/config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def crop_service(self):
        path_dir = str(load_qle.text())
        save_dir = str(save_qle.text())
        file_list = os.listdir(path_dir)

        max_size = 0
        for i in file_list:
            if i[len(i)-4:] == ".dcm":
                max_size = max_size+1

        self.serv_edt.append(str(max_size)+"개의 파일을 찾았습니다.")
        self.pbar.setMaximum(max_size)
        count = 0
        for i in file_list:
            if i[len(i)-4:] == ".dcm":
                count = count+1
                self.serv_edt.append(str(count)+"/"+str(max_size)+"번 작업 중...")
                img_data = pdcm.dcmread(path_dir + "/" + i)

                img_data.WindowCenter = 4095
                img_data.WindowWidth = 2048

                frame = apply_voi_lut(img_data.pixel_array, img_data)
                frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)
                frame = frame[30:frame.shape[0] - 30, 30:frame.shape[1] - 30]

                ret_low, frame_low = cv2.threshold(frame, 50, 255, 1)
                ret_hig, frame_hig = cv2.threshold(frame, 100, 255, 1)
                frame = cv2.bitwise_and(frame_low, frame_hig)

                kernel = np.ones((35, 35), np.uint8)
                frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)

                cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(np.uint8(frame))
                stats_T = stats.T

                min_size = (np.sum(stats_T[4])-stats_T[4][0])/(len(stats_T[4])-1)
                max_x = 0
                for j in range(1, cnt):
                    (x, y, w, h, area) = stats[j]
                    if 0 <= area-min_size and max_x <= x:
                        max_x = x

                line_x = 0

                for j in range(1, cnt):
                    (x, y, w, h, area) = stats[j]
                    if (x + w <= max_x and area > 50):
                        line_x = x + w

                final_x = int((max_x + line_x) / 2)

                origin_copy_R = pdcm.dcmread(path_dir + "/" + i)
                origin_copy_R.PixelData = origin_copy_R.pixel_array[:, 0:final_x + 50 + 30].tobytes()
                origin_copy_R.Columns = final_x + 50 + 30

                origin_copy_L = pdcm.dcmread(path_dir + "/" + i)
                origin_copy_L.PixelData = origin_copy_L.pixel_array[:,final_x - 50 - 30:origin_copy_L.Columns].tobytes()
                origin_copy_L.Columns = origin_copy_L.Columns - final_x + 50 + 30

                if not os.path.exists(save_dir+'/hand_R'):
                    os.mkdir(save_dir+'/hand_R')

                if not os.path.exists(save_dir+'/hand_L'):
                    os.mkdir(save_dir+'/hand_L')

                for j in range(1, cnt):
                    (x, y, w, h, area) = stats[j]
                    if (min_size >= area and area > 100):
                        if (x >= final_x):
                            origin_copy_L.save_as(save_dir+"/hand_R/R_" + i)
                            origin_copy_R.save_as(save_dir+"/hand_L/L_" + i)
                        else:
                            origin_copy_L.save_as(save_dir+"/hand_L/L_" + i)
                            origin_copy_R.save_as(save_dir+"/hand_R/R_" + i)
                        break
                self.pbar.setValue(count)
        self.serv_edt.append("작업이 완료되었습니다.")

def make_config():
    config = configparser.ConfigParser()

    username = getpass.getuser()
    save_dir = os.path.join("C:\\Users",username,"Desktop")
    load_dir = os.path.abspath('.')
    config['root'] = {}
    config['root']['load_dir'] = load_dir
    config['root']['save_dir'] = save_dir

    with open('./bin/config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
if __name__ == '__main__':
    if not os.path.isfile('./bin/config.ini'):
        make_config()
    app = QApplication(sys.argv)
    serv = Cropper()
    sys.exit(app.exec_())
